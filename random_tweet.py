from __future__ import annotations

import sys

from viceroybot.tweet import tweet_from_queue

tweet = tweet_from_queue(sys.argv[1])
print(tweet)
