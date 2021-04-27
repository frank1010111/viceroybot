import tweepy
import json
from viceroybot.auth_secrets import (
    BEARER_TOKEN,
    BEARER_TOKEN_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
)


def authenticate():
    # Authenticate to Twitter, returns API
    auth = tweepy.OAuthHandler(BEARER_TOKEN, BEARER_TOKEN_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def tweet_random(queue_file):
    "tweets the first unsent tweet from the queue file and sets it to sent"
    api = authenticate()

    with open(queue_file) as f:
        tweet_queue = json.load(f)
    for tweet in tweet_queue:
        if not tweet["sent"]:
            try:
                api.update_status(tweet["text"])
                tweet["sent"] = True
            except tweepy.TweepError:
                print("Failed to tweet")
            finally:
                break
    with open(queue_file, "w") as f:
        json.dump(tweet_queue, f)


def get_trending(location="USA"):
    if location == "USA":
        woeid = 23424977
    else:
        woeid = location
    api = authenticate()
    trends = [
        t["name"]
        for t in api.trends_place(woeid)[0]["trends"]
        if (
            (t["promoted_content"] is None)
            and (len(t["name"].split()) >= 3)  # nothing promoted
            # remove most people,
            # so I Nietzche doesn't shit-talk a dead hero of mine accidentally
        )
    ]
    return trends
