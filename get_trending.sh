#! /bin/bash
source /home/frank/anaconda3/bin/activate tweepy

MODEL=trained_model.pkl
QUEUE_FILE=tweet_queue.json
python viceroybot/predictor.py $MODEL -q $QUEUE_FILE --max_trends 4 && \
    echo "TWEET QUEUE EXPANDED"
