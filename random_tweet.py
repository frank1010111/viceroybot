from viceroybot.tweet import tweet_random
import sys

tweet = tweet_random(sys.argv[1])
print(tweet)
