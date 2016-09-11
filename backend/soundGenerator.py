import os
import math
import time

from pydub import *


def get_mood(text: str) -> str:
	questionmarks = text.count('?')
	exclamationmarks = text.count('!')
	multidots = text.count('..')

	exclamationmarks += text.count('?!')
	questionmarks -= text.count('?!')
	# Unwanted side-effect: "Hello!?!?" counts as exclamation, not as question

	caps = len([w for w in text.split() if w.isupper()])

	if caps + exclamationmarks > multidots + questionmarks:
		mood = 'aufgebracht'
	elif caps + exclamationmarks < multidots + questionmarks:
		mood = 'fragend'
	else:
		mood = 'neutral'

	return mood


def get_parent(path):
	return os.path.abspath(os.path.join(path, os.pardir))


HOT_ROOT = get_parent(get_parent(__file__))
SOUND_ROOT = os.path.join(HOT_ROOT, "ext", "sounds")
print("SOUND_ROOT = " + SOUND_ROOT)


def path_raw(bird: str, mood: str, retweet: bool):
	retweet_suffix = "-r" if retweet else ""
	# Goal: "mehlschwalbe-aufgebracht-r.mp3"
	filename = "{bird}-{mood}{suff}.mp3" \
		.format(bird=bird, mood=mood, suff=retweet_suffix)
	return os.path.join(SOUND_ROOT, filename)


def path_processed(bird: str, mood: str, retweet: bool, length: int):
	retweet_suffix = "-r" if retweet else ""
	# Goal: "processed/mehlschwalbe-aufgebracht-6000-r.mp3"
	filename = "{bird}-{mood}-{len}{suff}.mp3" \
		.format(bird=bird, mood=mood, len=length, suff=retweet_suffix)
	return os.path.join(SOUND_ROOT, 'processed', filename)


def find_pair(bird: str, mood: str, retweet: bool, length: int):
	candidates = [(bird, mood, retweet),
				  (bird, 'neutral', retweet),
				  ('amsel', 'neutral', False)]
	verbose = False
	for (b, m, r) in candidates:
		candidSource = path_raw(b, m, r)
		if os.path.isfile(candidSource):
			if verbose:
				print("[INFO] Found at {}".format(candidSource))
			return candidSource, path_processed(b, m, r, length)
		else:
			print("[WARN] Source file {} missing, falling back …".format(candidSource))
			verbose = True
	print("[ERR ] All sources and fallbacks missing.  Giving up.")
	return None


# Let's hope that the backend doesn't get started twice within a second
STARTUP = str(int(time.time() * 1000))

processed_tweets = 0


class SoundGenerator:
	def __init__(self):
		self.soundDir = self.getSoundDir()


	### directories and files ###

	def getParent(self, dirr):
		return os.path.abspath(os.path.join(dirr, os.pardir))

	def getSoundDir(self):
		extSounds = os.path.sep + "ext" + os.path.sep + "sounds"
		hotRoot = self.getParent(__file__)
		return os.path.abspath(os.path.join(hotRoot, os.pardir)) + extSounds

	def getFileName(self, bird, mood, retweet):
		if retweet == False:
			return str(bird) + "-" + mood + ".mp3"
		else:
			return str(bird) + "-" + mood + "-r.mp3"

	def getSoundPath(self, bird, mood, retweet):
		return self.soundDir + os.path.sep + self.getFileName(bird, mood, retweet)

	def soundExists(self, bird, mood, retweet):
		print("SoundExists " + self.getSoundPath(bird, mood, retweet) + "   " + str(os.path.isfile(self.getSoundPath(bird, mood, retweet))))
		return os.path.isfile(self.getSoundPath(bird, mood, retweet))


	### sound handling ###

	def makeSounds(self, tweetid, content, isRetweet, cBird, pBird):
		mood = get_mood(content)

		if pBird is not None:
			pMood = self.getClosestMood(pBird, mood, isRetweet)
		
		cMood = self.getClosestMood(cBird, mood, isRetweet)

		if pBird is not None:
			pPath = self.getSoundPath(pBird, pMood, isRetweet)
		cPath = self.getSoundPath(cBird, cMood, isRetweet)

		pRes = None
		pdur = 0
		if pBird is not None:
			(pRes, pdur) = self.createNewSoundfile(pBird, pMood, isRetweet, len(content), tweetid, 'p')
		
		(cRes, cdur) = self.createNewSoundfile(cBird, cMood, isRetweet, len(content), tweetid, 'c')

		return(pRes, cRes, pdur, cdur)

	def getClosestMood(self, bird, mood, retweet):
		n = 'neutral'
		a = 'aufgebracht'
		f = 'fragend'
		nExists = self.soundExists(bird, n, retweet)
		aExists = self.soundExists(bird, a, retweet)
		fExists = self.soundExists(bird, f, retweet)

		err = "No suitable sound file for " + bird + " found."
		
		if self.soundExists(bird, mood, retweet):
			return mood
		elif mood == 'neutral':
			if fExists:
				return f
			elif aExists:
				return a
			else:
				print(err)
		elif mood == 'aufgebracht':
			if nExists:
				return n
			elif fExists:
				return f
			else:
				print(err)
		elif mood == 'fragend':
			if nExists:
				return n
			elif aExists:
				return a
			else:
				print(err)
		else:
			print(mood + "is not an accepted mood. Accepted moods are: neutral, aufgebracht, fragend")

	def createNewSoundfile(self, bird, mood, retweet, length, tweetid, group):
		finDuration = max(length * 250, 6000)
		sound = AudioSegment.from_mp3(self.getSoundPath(bird, mood, retweet))
		origDuration = math.floor(sound.duration_seconds)*1000
		print("original: " + str(origDuration))
		print("final: " + str(finDuration))
		print(str(finDuration > origDuration))
		if finDuration < origDuration:
			middle = math.floor(origDuration/2)
			print("middle: " + str(middle))
			print("first length: " + str(middle + math.floor(finDuration/2)))
			sound = sound[:(middle + math.floor(finDuration/2))]
			sound = sound[-math.floor(finDuration):]
		sound = sound.fade_in(2000).fade_out(2000)
		global processed_tweets
		path = self.soundDir + os.path.sep + "processed/" + STARTUP + "_" + str(processed_tweets) + ".mp3"
		processed_tweets += 1
		sound.export(path, format="mp3")
		return (path, finDuration)


def generate_sound(content: str, retweet: bool, birds):
	# Why is that even a class?  FIXME: dissolve 'SoundGenerator' into functions
	sg = SoundGenerator()
	_, pBird = (b.replace('ß','ss') if b is not None else None for b in birds)
	# return sg.makeSounds(STARTUP, content, retweet, cBird, pBird)
	dummy = sg.getSoundPath('amsel', 'neutral', False)
	bird = {'natural': dummy, 'synth': dummy}
	return {'duration': 6000, 'citizen': bird, 'poli': bird if pBird is not None else None}
"""
- `sound`: JSON object
    - `duration`: integer, length, in milliseconds, of the sounds
    - `citizen`: JSON object, describing the bird chosen by the citizen
        - `natural`: string, valid path to the bird's natural sound, e.g. `"/home/eispin/workspace/House-Of-Tweets/ext/sounds/processed/774316458742583296r-c_n.mp3"`
        - `synth`: string, valid path to the bird's "synthesized" sound or "artistic interpretation", e.g. `"/home/eispin/workspace/House-Of-Tweets/ext/sounds/processed/774316458742583296r-c_s.mp3"`
    - `poli`: same, but chosen by the politician.  If not a politician, `null`.
"""
