House of Tweets
===============

<!-- Do not change the first three lines; it is used by provide.sh to verify
     stuff.  Also, HTML comments need to stand alone. -->

House of Tweets is an art/computer science project that took place at the Saarland University.

We do not want to bother anyone with unnecessarily many words, so feel free to play around with our project and leave feedback if you like. Make sure, your sound is turned on!

![main_page_overview](https://github.com/Schwenger/House-Of-Tweets/blob/master/preview.png)


Install instructions:
=====================

For the tersest but also most platform-specific instructions, read the `.travis.yml` script.

### Get all secrets

If you're one of us, then you have access to the repository referenced
in `.gitmodules`, and all you need to do is `git submodule update
--init .secrets`.

If not, you should probably overwrite the `credentials.py` with a short Python "module" that defines a map `CREDENTIALS`.
- the format is pretty obvious
- see `credentials_TEMPLATE.py` for an example

### Get heavy

You'll need the heavy files stored in `.heavy`, so so a `git submodule update --init .heavy`

Or just update all submodules in one go with `git submodule update --init`

### OS-dependent packages

In general, you'll need:
- some form of libav for pydub (see below)
- npm
- rabbitmq
- coffeescript
- Python 3
- pip (sometimes "pip3", should be running on Python 3)
- script (as in "typescript", appeared in BSD 3.0)

Install like this:
- Ubuntu: `sudo apt-get install -qq libav-tools npm rabbitmq-server coffeescript` (python, pip, and bsdutils?)
- Debian: `sudo apt-get install -qq libav-tools npm rabbitmq-server coffeescript python3-dev python3-pip bsdutils`
- MacOS X: `brew install rabbitmq node python3 libav bsdutils`
Afterwards add the following to your `.bashrc`
```
export NODE_PATH=/usr/local/lib/node_modules
```
Then, run `npm install -g coffee-script`.

Some systems (Ubuntu and Debian, at least) install the `node` binary in
a way that is incompatible with npm.  To resolve this, do this on
Debian and Ubuntu:
```
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

### OS-independent packages

Frontend-dependencies will be installed automatically by running
`make install_dependencies`.
This will essentially run
```
npm install --prefix=./ext/ stompjs browserify coffeescript-concat less
pip3 install pika pydub tweepy typing
```

Note that Ubuntu calls it `pip`.
Check with `--version` which Python version it is addressing.

Note that under Debian, you may need to install the pip packages as sudo.


Normal workflow:
================

Get RabbitMQ running:
- preconditions: none
- if not already started: `sudo rabbitmq-server -detached` (the `-detached` part starts it "into the background")
- wait a second (RabbitMQ doesn't like being rushed at this point)
- load plugin: `sudo rabbitmq-plugins enable --online rabbitmq_web_stomp rabbitmq_management`  
  Explanation:
    * `--online` means: fail if rabbitmq isn't running
    * `rabbitmq_web_stomp` enables communication with the frontend
    * `rabbitmq_management` is optional, and provides [a web interface](http://localhost:15672)
- useful for: running the project, running tests

Build the frontend:
- preconditions: none
- execute: `make frontend` or just `make`
- useful for: running the project

Run the backend:
- preconditions: RabbitMQ is running
- start: `( cd backend && ./backend.py )`
- useful for: running the project

Run the tests:
- preconditions: RabbitMQ is running (unless you changed `MANUAL_TESTS` in `tests.py`)
- start: `( cd backend && ./tests.py )`

Run the project / presentation:
- preconditions: backend and RabbitMQ are running
- start: point your browser at `out/main.html`


Authors:
========

* Michaela Klauck (s9miklau@stud.uni-saarland.de)
* Christopher Schommer (s9crscho@stud.uni-saarland.de)
* Maximilian Schwenger (schwenger@stud.uni-saarland.de)
* s9saster@stud.uni-saarland.de
* Ben Wiederhake (s9bewied@stud.uni-saarland.de, Ben.Wiederhake@gmail.com)

Sounds are extracted from [xeno-canto](http://www.xeno-canto.org/about/terms), thank you very much!
Images can be extracted from wikipedia, for legal reasons, they are not included online.


Troubleshooting:
================
In case there are any troubles running the application on windows, we are aware of this but we do not intend to fix it. The application is designed for unix systems.
