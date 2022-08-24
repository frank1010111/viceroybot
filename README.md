# ViceroyBot

[![License](https://img.shields.io/badge/License-BSD_3--Clause-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Twitter bot for mimicking writing.

The method for mimicking writing comes from the classic textbook
[The Practice of Programming](https://www.cs.princeton.edu/~bwk/tpop.webpage/)
and uses a Markov Chain algorithm that the book implements in several different
languages.

Now, sure, you can use this without the twitter functionality, but where's the
fun in that?

## Using this package

First, clone this repository with

```
git clone https://github.com/frank1010111/viceroybot.git
cd viceroybot
pip install .
```

Next, you'll need some writings. Sure, you could grab a bunch of tweets, but
maybe you'd prefer to improve the discourse of that august site. I recommend
grabbing something from [Project Gutenberg](https://www.gutenberg.org/). Save
them in the `txt` folder.

Then train the Markov chain model with

```
viceroy train txt/*
```

If you want to stop here, you can do things like

```
viceroy generate Little is lacking
```

But if you want to use twitter, you've got to get set up with authentication.
The authentication comes from the
[Twitter Developer Portal Projects and Apps page](https://developer.twitter.com/en/portal/projects-and-apps).

Copy those into the `.env` file like so:

```
export VICEROY_LOCATION=".viceroy"
export BEARER_TOKEN=""
export BEARER_TOKEN_SECRET=""
export ACCESS_TOKEN=""
export ACCESS_TOKEN_SECRET=""
```

It's great fun. Tweepy gets into the
[authentication](https://docs.tweepy.org/en/stable/authentication.html#authentication)
in more detail.

Then you can start building a tweet queue with the command

```
viceroy queue
```

By default it will take US trending topics and write a tweet about one. You can
send this tweet with

```
viceroy tweet
```

And that's how it goes!
