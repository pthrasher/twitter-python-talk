import redis
import json
import datetime
import hydrators
import events


HYDRATORS = [
    hydrators.user_data,
    hydrators.body,
    hydrators.lat_lon,
]

EVENTS = {
    "simple_tweet": events.simple_tweet,
    "geo_blip": events.geo_blip,
}


def log_tweet(username, name, tweet_body):
    now = datetime.datetime.now()
    print "[%s] @%s (%s): %s" % (now, username, name, tweet_body,)


def consume_raw_subscription(tweets):
    """
    This method consumes the raw tweets, parses them, hands them to each
    hydrator, the hydrator cleans the data, then we run through a list of event
    handlers, each of which will publish to a redis queue if it has the data it
    needs.
    """
    while True:
        message = tweets.next()

        raw_tweet = message.get('data')
        if not raw_tweet:
            continue

        try:
            tweet = json.loads(raw_tweet)
        except ValueError, e:
            continue

        # Sometimes we just get back spurious data, like integers and stuff
        if not isinstance(tweet, dict):
            continue

        # Data extraction
        clean_obj = {}

        for hydrator in HYDRATORS:
            # Allow the method to overwrite our clean data
            hydrated = hydrator(tweet, clean_obj)
            if hydrated:
                clean_obj.update(hydrated)

        for kind, fn in EVENTS.items():
            # Publish events
            data = fn(clean_obj)
            json_data = json.dumps(data)
            event = json.dumps({
                'kind': kind,
                'body': json_data,
            })
            redis.publish('events', event)


if __name__ == '__main__':
    try:
        redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        pubsub = redis.pubsub()
        pubsub.subscribe('twitter_raw')
        tweets = pubsub.listen()
        consume_raw_subscription(tweets)

    except KeyboardInterrupt:
        print "\nBye!"
