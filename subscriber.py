"""
This file is only used for step-2
"""
import redis
import json
import datetime


def log_tweet(username, name, tweet_body):
    now = datetime.datetime.now()
    print "[%s] @%s (%s): %s" % (now, username, name, tweet_body,)


def consume_subscription(tweets):
    while True:
        message = tweets.next()

        raw_tweet = message.get('data')
        if not raw_tweet:
            continue

        tweet = json.loads(raw_tweet)

        # Sometimes we just get back spurious data, like integers and stuff
        if not isinstance(tweet, dict):
            continue

        # Data extraction
        tweet_body = tweet.get('text')
        user = tweet.get('user', {})
        username = user.get('screen_name')
        name = user.get('name')

        # Data presentation
        if tweet_body and name and username:
            log_tweet(username, name, tweet_body)


if __name__ == '__main__':
    try:
        redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        pubsub = redis.pubsub()
        pubsub.subscribe('twitter_raw')
        tweets = pubsub.listen()
        consume_subscription(tweets)

    except KeyboardInterrupt:
        print "\nBye!"
