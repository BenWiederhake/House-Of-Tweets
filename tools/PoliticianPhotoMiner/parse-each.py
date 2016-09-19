#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json

TWITTER_PREFIX = 'https://twitter.com/'


# Even more code duplication.
# I'm not sure whether this still is a good idea.

def get_details_bundestag(old_entry, soup):
    assert old_entry['src'] == 'bundestag'
    entry = dict()
    entry['src'] = old_entry['src']
    entry['page'] = old_entry['page']
    entry['full_name'] = old_entry['full_name']
    entry['img'] = None  # Force JSON null
    entry['twitter_handle'] = None  # Force JSON null
    entry['ejected'] = False
    detect_party = old_entry['detect_party']
    if detect_party.endswith(' *'):
        # Parties like 'SPD *' mean: no longer in the Bundestag.
        entry['possible_parties'] = []
        # soup = BeautifulSoup()
        bio = soup.find('div', 'biografie')
        if bio is None or not bio.get_text().strip().endswith('ausgeschieden'):
            print('WARN: {} apparently left: {}'.format(entry['full_name'], entry['page']))
            print('  … and text says something different?')
            assert False
        detect_party = detect_party[:-2]
        entry['ejected'] = True

    if detect_party == 'Die Linke':
        entry['possible_parties'] = ['die linke']
    elif detect_party == 'CDU/CSU':
        entry['possible_parties'] = ['cdu', 'csu']
    elif detect_party == 'SPD':
        entry['possible_parties'] = ['spd']
    elif detect_party == 'B\u00fcndnis 90/Die Gr\u00fcnen':
        entry['possible_parties'] = ['gruene']
    else:
        assert False, "Unknown party: '{}'".format(old_entry['detect_party'])
    return entry


def get_details_linke(old_entry, soup):
    assert old_entry['src'] == 'die linke'
    entry = dict()
    entry['src'] = old_entry['src']
    entry['page'] = old_entry['page']
    entry['full_name'] = old_entry['full_name']
    # No 'ejected'
    entry['possible_parties'] = [old_entry['src']]
    imgdata = {'license': 'unknown-linke'}

    # Twitter-Handle
    # <a href="https://twitter.com/AndrejHunko">Twitter-Profil</a>
    for a in soup.find_all('a'):
        href = a.get('href')
        if href is None or not href.startswith(TWITTER_PREFIX):
            # Not even relevant
            continue
        raw_text = a.get_text()
        if raw_text == '':
            continue
        assert raw_text == 'Twitter-Profil', (a, old_entry)
        new_handle = href[len(TWITTER_PREFIX):]
        assert 'twitter_handle' not in entry, (entry['twitter_handle'], new_handle, old_entry)
        entry['twitter_handle'] = new_handle
        # Don't break: check/assert for duplicate links!
    # Don't assert: omission is okay

    # Image:
    # <a href="/fileadmin/user_upload/Pressefotos/pressefoto-jan-van-aken.jpg"
    #    target="_blank">Pressefoto von Jan van Aken</a>
    # Duplicate effort, but whatever.  Ease of readability ftw!
    for a in soup.find_all('a'):
        PREFIX = '/fileadmin/user_upload/Pressefotos/pressefoto-'
        href = a.get('href')
        good_text = a.get_text().startswith('Pressefoto von ')
        good_href = href is not None and href.startswith(PREFIX)
        if not good_text and not good_href:
            continue
        assert good_text and good_href, (a, old_entry)
        new_url = 'https://www.linksfraktion.de' + href
        assert 'url' not in imgdata, (imgdata['url'], new_url, old_entry)
        imgdata['url'] = new_url
        # Don't break: check/assert for duplicate links!
    assert 'url' in imgdata

    entry['img'] = imgdata
    return entry


def get_details_gruene(old_entry, soup):
    assert old_entry['src'] == 'gruene'
    entry = dict()
    entry['src'] = old_entry['src']
    entry['page'] = old_entry['page']
    entry['full_name'] = old_entry['full_name']
    # No 'ejected'
    entry['possible_parties'] = [old_entry['src']]
    imgdata = {'license': 'unknown-gruene', 'is_compressed': True}

    # Twitter-Handle
    # <a href="https://twitter.com/Luise_Amtsberg" target="_blank"
    #    class="share__button share__button--twitter--outline">Twitter</a>
    twitter_a = soup.find('a', 'share__button--twitter--outline')
    if twitter_a is not None:
        href = twitter_a.get('href')
        # Dear Grüne,
        # please get your shit together.
        # https://www.youtube.com/watch?v=jl17CYYSzUw
        href = href.replace('http://', 'https://')
        href = href.replace('//www.twitter.com/', '//twitter.com/')
        assert href.startswith(TWITTER_PREFIX), (href, old_entry)
        new_handle = href[len(TWITTER_PREFIX):]
        entry['twitter_handle'] = new_handle

    # Image:
    # <a href="uploads/tx_wwgruenefraktion/Amtsberg_Luise_01.zip"
    #    class="member-media__download">Download Foto</a>
    for a in soup.find_all('a', 'member-media__download'):
        PREFIX = 'uploads/tx_wwgruenefraktion/'
        href = a.get('href')
        good_text = a.get_text() == 'Download Foto'
        good_href = href is not None and href.startswith(PREFIX)
        if not good_text and not good_href:
            continue
        assert good_text and good_href, (a, old_entry)
        # https://www.gruene-bundestag.de/uploads/tx_wwgruenefraktion/Franziska-Branter.zip
        new_url = 'https://www.gruene-bundestag.de/' + href
        assert 'url' not in imgdata, (imgdata['url'], new_url, old_entry)
        imgdata['url'] = new_url
        # Don't break: check/assert for duplicate links!
    assert 'url' in imgdata

    entry['img'] = imgdata
    return entry


def get_details_spd(old_entry, soup):
    assert old_entry['src'] == 'spd'
    entry = dict()
    entry['src'] = old_entry['src']
    entry['page'] = old_entry['page']
    entry['full_name'] = old_entry['full_name']
    # No 'ejected'
    entry['possible_parties'] = [old_entry['src']]
    imgdata = {'license': 'custom-spd'}
    entry['img'] = imgdata

    # Twitter-Handle
    # <a href="https://twitter.com/NielsAnnen" target="_blank">twitter</a>
    for a in soup.find_all('a'):
        href = a.get('href')
        if href is None or not href.startswith(TWITTER_PREFIX):
            # Not even relevant
            continue
        raw_text = a.get_text()
        if 'http://www.spdfraktion.de' in href or \
           'search?q=' in href or \
           'http%3A%2F%2Fwww.spdfraktion.de%2F' in href or \
           raw_text.startswith('@'):
            # Dumb header-things.  What the hell?
            continue
        if raw_text != 'twitter':
            print('ignore {}: {}'.format(a, old_entry))
            continue
        new_handle = href[len(TWITTER_PREFIX):]
        assert 'twitter_handle' not in entry, (entry['twitter_handle'], new_handle, old_entry)
        entry['twitter_handle'] = new_handle
        # Don't break: check/assert for duplicate links!
    # Don't assert: omission is okay

    # You're a special snowflake, aren't you?
    # http://www.spdfraktion.de/abgeordnete/mierscheid?wp=18
    if entry['full_name'] == 'Jakob Maria Mierscheid':
        # Spoof something so that the crawler doesn't need special rules.
        imgdata['url'] = 'file:///dev/null'
        imgdata['copyright'] = '/dev/null'
        return entry

    # Image:
    # <a title="Bild-Download" href="http://www.spdfraktion.de/system/files/images/annen_niels.jpg"
    #    class="ico_download float_right">Pressebild (4249 KB)</a>
    img_a = soup.find('a', 'ico_download')
    assert img_a is not None, old_entry
    img_href = img_a.get('href')
    assert img_href.startswith('http://www.spdfraktion.de/system/files/images/'), (img_href, old_entry)
    assert img_a.get_text().startswith('Pressebild (')
    # https://www.gruene-bundestag.de/uploads/tx_wwgruenefraktion/Franziska-Branter.zip
    imgdata['url'] = img_href

    # Photographer:
    # <span class="copyright">(Foto: spdfraktion.de (Susie Knoll / Florian Jänicke))</span>
    copyright = soup.find('span', 'copyright')
    assert copyright is not None
    copy_text = copyright.get_text()
    COPY_START = '(Foto: '
    COPY_END = ')'
    assert copy_text.startswith(COPY_START) and copy_text.endswith(COPY_END), (copy_text, old_entry)
    copy_text = copy_text[len(COPY_START):]
    copy_text = copy_text[:-len(COPY_END)]
    imgdata['copyright'] = copy_text

    return entry


def get_details_cxu(old_entry, soup):
    raise NotImplementedError()


def get_details_all(entries):
    # Setup
    detailers = {
        #'bundestag': get_details_bundestag,
        #'die linke': get_details_linke,
        'gruene': get_details_gruene,
        #'spd': get_details_spd,
        #'cxu': get_details_cxu,
    }
    # Actual work
    for e in entries:
        detailer = detailers.get(e['src'])
        if detailer is None:
            print('[WARN] skip for party {}: {}'.format(e['src'], e['full_name']))
            continue
        with open(e['page_file'], 'r') as fp:
            the_soup = BeautifulSoup(fp.read(), 'html.parser')
        yield detailer(e, the_soup)


if __name__ == '__main__':
    # Reading
    with open('crawl-each.json', 'r') as json_fp:
        all_entries = json.load(json_fp)

    # Parsing
    detailed = list(get_details_all(all_entries))

    # Write it out.
    with open('parse-each.json', 'w') as fp:
        json.dump(detailed, fp, sort_keys=True, indent=2)
    print('Done.')
