"""Work with twitter to authenticate, get trending tweets, and send random tweets."""

from __future__ import annotations

import json
import os
from datetime import datetime

import tweepy
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
BEARER_TOKEN_SECRET = os.environ.get("BEARER_TOKEN_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")


def authenticate():
    """Authenticate to Twitter, returns API."""
    auth = tweepy.OAuthHandler(BEARER_TOKEN, BEARER_TOKEN_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def tweet_from_queue(queue_file):
    """Tweet the first unsent tweet from the queue file and set it to sent."""
    api = authenticate()

    with open(queue_file) as f:
        tweet_queue = json.load(f)
    for tweet in tweet_queue:
        if not tweet["sent"]:
            try:
                api.update_status(tweet["text"])
                tweet["sent"] = datetime.now().strftime("%Y-%m-%d %T")
                break
            except tweepy.TweepError as e:
                raise e
    else:
        raise ValueError("No tweets left in queue")
    with open(queue_file, "w") as f:
        json.dump(tweet_queue, f, indent=2)
    return tweet["text"]


def get_trending(location: str | int = "USA", min_words: int = 3):
    """Get trending tweets for a location from twitter.

    See <https://github.com/vishnumohanrk/twitter-WOEID> for the WOEID list.

    Args:
        location (str | int): twitter location (USA or a woeid)
        min_words (int): minimum number of words

    Returns:
        list of trending topics
    """
    if location == "USA":
        woeid = 23424977
    else:
        woeid = location
    api = authenticate()
    trends = [
        t["name"]
        for t in api.get_place_trends(woeid)[0]["trends"]
        if (
            (t["promoted_content"] is None)  # nothing promoted
            and (len(t["name"].split()) >= min_words)
        )
    ]
    return trends
