# IMPORTS

import re
import string
import tweepy
import nltk
nltk.download('punkt')
import nltk.classify
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# import json


# SET UP TWITTER
# with open('twitter_auth.json') as f:
#    keys = json.load(f)

consumer_key = "3KAOEpQrsfcxOuPboqi38FmFY0"
consumer_secret = "YqWkfAiJA2jo2oV6lrME9P4cofizwIkSPK6vHDpF7XMuCAY3qv"
access_token = "1125943090240479232-iHH9O5ISz6lKAu6lsjbYDzIpnJ9egR"
access_token_secret = "bGRWGIKwr105Thhpo8gUbj8I8hNn3DWITH5Kucz9KK061"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

tweets = []


# TWITTER STREAM
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        tweets.append(status.text.rstrip())
        if len(tweets) > 200:
            myStream.disconnect()


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

# myStream.filter(track=["christmas"], languages=['en'])
# print(tweets[0])

pos_emojis = ['😙','❤','😍','💓','😗','☺','😊','😛','💕','😀','😃','😚']
neg_emojis = ['☹','😕','😩','😒','😠','😐','😦','😣','😫','😖','😞','💔','😢','😟']
all_emojis = ['😙','❤','😍','💓','😗','☺','😊','😛','💕','😀','😃','😚','☹','😕','😩','😒','😠','😐','😦','😣','😫','😖','😞','💔','😢','😟']

# Fetch some tweets
myStream.filter(track=all_emojis, languages=['en'])


# Store some tweets
def store_tweets(file, tweets):
    # open file being passed in
    with open(file, 'r') as f:
        old_tweets = f.readlines()
    # load all tweets
    all_tweets = old_tweets + tweets
    # remove duplicates by transforming to set
    all_tweets = list(set(all_tweets))
    # remove newlines
    all_tweets = [tweet.replace('\n','')+"\n" for tweet in all_tweets]

    # write list to file
    with open('tweets.txt', 'w') as f:
        f.writelines(all_tweets)

    return all_tweets

# Clean up tweets
def clean_tweets(tweets):
    # remove @ and http with list comprehension
    tweets = [re.sub(r'http\S+', '', tweet) for tweet in tweets]
    tweets = [re.sub(r'@\S+', '', tweet) for tweet in tweets]
    tweets = [tweet.translate({ord(char): ' ' for char in string.punctuation}) for tweet in tweets]
    tweets = [tweet.rstrip() for tweet in tweets]

    return tweets

# Sorting tweets
def sort_tweets(tweets):
    positive_tweets = [tweet for tweet in tweets if set(tweet) & set(pos_emojis)]
    negative_tweets = [tweet for tweet in tweets if set(tweet) & set(neg_emojis)]

    positive_tweets = [re.sub(r'[^\x00-\x7f]+','', tweet) for tweet in positive_tweets]
    negative_tweets = [re.sub(r'[^\x00-\x7f]+','', tweet) for tweet in negative_tweets]

    return positive_tweets, negative_tweets


#
def parse_tweets(words):
    words = words.lower()
    # split up into a list of words
    words = word_tokenize(words)
    # remove words without meaning
    words = [word for word in words if word not in stopwords.words('english')]
    word_dictionary = dict([(word, True) for word in words])

    return word_dictionary


def train_classifier(positive_tweets, negative_tweets):
    # Create tuples
    positive_tweets = [(parse_tweets(tweet),'positive') for tweet in positive_tweets]
    negative_tweets = [(parse_tweets(tweet),'negative') for tweet in negative_tweets]

    # fraction of tweets for training
    fraction_pos = round(len(positive_tweets) * 0.8)
    fraction_neg = round(len(negative_tweets) * 0.8)

    # add all of the training tweets together and determine accuracy
    train_set = negative_tweets[:fraction_pos] + positive_tweets[:fraction_pos]
    test_set = negative_tweets[fraction_neg:] + positive_tweets[fraction_neg:]
    classifier = NaiveBayesClassifier.train(train_set)
    accuracy = nltk.classify.util.accuracy(classifier, test_set)

    return classifier, accuracy


## EXECUTE THE PROGRAM
tweets = store_tweets('tweets.txt', tweets)
# print(tweets[1])
tweets = clean_tweets(tweets)
# print(tweets[1])
pos_tweets, neg_tweets = sort_tweets(tweets)
classifier, accuracy = train_classifier(pos_tweets, neg_tweets)
