#! /bin/bash
#source /home/frank/anaconda3/bin/activate tweepy

QUEUE_FILE=.viceroy/tweet_queue.json
python random_tweet.py $QUEUE_FILE && \
    echo "RANDOM TWEET SENT"
