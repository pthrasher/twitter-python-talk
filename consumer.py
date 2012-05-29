import tweepy
import redis
from twitter_credentials import *


class Listener(tweepy.StreamListener):
    def on_data(self, data):
        if data: # don't worry about blank lines
            redis.publish('twitter_raw', data)


if __name__ == '__main__':
    try:
        """
        The following need to be specified in './twitter_credentials.py'
        CONSUMER_KEY
        CONSUMER_SECRET
        ACCESS_TOKEN
        ACCESS_TOKEN_SECRET
        """
    
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        streaming_api = tweepy.streaming.Stream(auth, Listener(), timeout=60)
        # Geo box that covers the entire earth to ensure we only get geo-located tweets
        streaming_api.filter(locations=[ -180,-90,180,90 ])
    except KeyboardInterrupt:
        print "\nBye!"
