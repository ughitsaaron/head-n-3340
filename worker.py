import boto3
import html
import os
import random
import re
import twitter
import urllib.request

""" Program requests a collection of tweets containing the
phrase "i wish i" then filters, formats, and concatenates the
results to a text file stored on Amazon and hosted on the web
at https://head-n-3340.herokuapp.com
"""

bucket = "personalprojects.aaronpetcoff"
key = "head-n-3340/main.txt"
s3 = boto3.resource("s3")
url = "https://s3.amazonaws.com/" + bucket + "/" + key

# grab api keys from environment
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
token_key = os.environ.get("ACCESS_KEY")
token_secret = os.environ.get("TOKEN_SECRET")

# get awful words to filter from environment
filter_words = os.environ.get("AWFUL_WORDS").split()


def collect_tweets(results, wishes=set(), max=12):
    """ creates a set of tweets
    """
    tweet = pick_tweet(results)

    if len(wishes) < max:
        wishes.add(format_tweet(tweet.text))
        return collect_tweets(results, wishes)

    return wishes


def pick_tweet(results):
    # grab a random value from results and filter it
    tweet = filter_awful_stuff(random.choice(results))

    # reject the tweet if any of these conditions are met
    validations = [
        len(tweet.user_mentions) > 0,  # mentions
        len(tweet.urls) > 0,  # links
        tweet.media,  # media
        "i wish i" not in tweet.text.lower()  # doesn"t have "i wish i"
    ]

    if any(validations):
        # if any of the values in `validations` are true
        # run the function again recursively
        return pick_tweet(results)

    # return the tweet if it has value after being filtered
    return tweet if tweet else pick_tweet(results)


def format_tweet(tweet):
    text = tweet
    patterns = [
        "\#\w+",  # removes hashtags
        "[^\u0000-\u007F]",  # removes emoji
        "\"$"  # tries to remove hanging quotation marks
    ]

    for pattern in patterns:
        # iterate over each pattern and substitue it with an empty string
        # successively writing the value to `text`
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return html.unescape(re.search("i wish i?.*", text, re.IGNORECASE).group())


def filter_awful_stuff(tweet):
    for word in filter_words:
        return None if word in tweet.text else tweet


api = twitter.Api(consumer_key, consumer_secret, token_key, token_secret)
results = api.GetSearch(term="\"i wish i\"", result_type="recent", count=100)


def cron():
    """ create cron scheduled to fetch tweets
    twice a day every day and push them to the
    text file on S3
    """
    print("Cron started…")

    with urllib.request.urlopen(url) as text:
        print("Fetching data…")
        output = "\n".join(list(collect_tweets(results))) + "\n"
        data = text.read() + bytes(output, "utf-8")
        s3.Bucket(bucket).put_object(Key=key, Body=data)  # upload
        s3.Object(bucket, key).Acl().put(ACL="public-read")  # make public
        print("Data fetched…")


if __name__ == "__main__":
    cron()
