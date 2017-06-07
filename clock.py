import twitter
import random
import os
import re
import html
import urllib.request
import boto3
from apscheduler.schedulers.blocking import BlockingScheduler

""" Program requests a collection of tweets containing the phrase "i wish i" then filters, formats, and concatenates the results to
a text file stored on Amazon
"""

s3 = boto3.resource("s3")
bucket = "personalprojects.aaronpetcoff"
key = "head-n-3340/main.txt"
url = "https://s3.amazonaws.com/" + bucket + "/" + key

sched = BlockingScheduler()

# grab api keys from environment
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
token_key = os.environ.get("ACCESS_KEY")
token_secret = os.environ.get("TOKEN_SECRET")

def collect_tweets(results, wishes = set(), max = 12):
    """ recursively creates a set of tweets with
        a length equal to max. i use a set instead
        of a list in order to avoid duplicate values
    """
    tweet = pick_tweet(results)

    if len(wishes) < max:
        wishes.add(format_tweet(tweet.text))
        return collect_tweets(results, wishes)
    else:
        return wishes

def pick_tweet(results):
    # grab a random value from results and filter it
    tweet = filter_awful_stuff(random.choice(results))

    validations = [
        len(tweet.user_mentions) > 0, # skip the tweet if it contains mentions
        len(tweet.urls) > 0, # skip the tweet if it contains links
        tweet.media, # skip the tweet if it contains media
        not "i wish i" in tweet.text.lower() # the query should ensure the phrase is in the tweet text, but sometimes something sneaks thru
    ]

    if any(validations):
        # if any of the values in `validations` are true
        # run the function again recursively
        return pick_tweet(results)

    # return the tweet if it has value after being filtered
    return tweet if tweet else pick_tweet(results)

def format_tweet(tweet):
    """ formats tweet according to the regular expressions
        defined in `patterns`
    """
    text = tweet
    patterns = [
        "\#\w+", # removes hashtags
        "[^\u0000-\u007F]", # removes emoji
        "\"$" # tries to remove hanging quotation marks
    ]

    for pattern in patterns:
        # iterate over each pattern and substitue it with an empty string
        # successively writing the value to `text`
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return html.unescape(re.search("i wish i?.*", text, re.IGNORECASE).group())

def filter_awful_stuff(tweet):
    # i'm not sure how likely these are to pop up
    # but i just don't want them here. the poem will
    # collect enough terrible shit without them
    for word in ["nigger", "rape", "faggot", "whore"]:
        return None if word in tweet.text else tweet

api = twitter.Api(consumer_key, consumer_secret, token_key, token_secret)

results = api.GetSearch(term="\"i wish i\"", result_type="recent", count=100)

def cron():
    with urllib.request.urlopen(url) as text:
        output = "\n".join(list(collect_tweets(results)))
        data = text.read() + bytes(output + "\n", "utf-8")
        print()
        s3.Bucket(bucket).put_object(Key=key, Body=data) # upload
        s3.Object(bucket, key).Acl().put(ACL="public-read") # make public

sched.add_job(cron, 'cron', day_of_week='mon-sun', hour='0')
sched.add_job(cron, 'cron', day_of_week='mon-sun', hour='12')

sched.start()
