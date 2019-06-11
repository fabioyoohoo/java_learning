# created 6-10-2019
# source: https://projects.raspberrypi.org/en/projects/naughty-and-nice/9

import re
import string
import tweepy
import nltk

import nltk.classify
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import json


# SET UP TWITTER
# load json file with authentication
with open('twitter_auth.json') as f:
    keys = json.load(f)

consumer_key = keys['consumer_key']
consumer_secret = keys['consumer_secret']
access_token = keys['access_token']
access_token_secret = keys['access_token_secret']

# set up authentication handles
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# empty list to store new 200 tweets
tweets = []


# TWITTER STREAM
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        tweets.append(status.text.rstrip())
        if len(tweets) > 200:
            myStream.disconnect()


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)

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
    # change all words to lower
    words = words.lower()
    # split up into a list of words
    words = word_tokenize(words)
    # remove words without meaning (prep, conj, etc.)
    words = [word for word in words if word not in stopwords.words('english')]
    # adds words to dictionary that have meaning
    word_dictionary = dict([(word, True) for word in words])

    return word_dictionary


def train_classifier(positive_tweets, negative_tweets):
    # Create tuples
    positive_tweets = [(parse_tweets(tweet),'positive') for tweet in positive_tweets]
    negative_tweets = [(parse_tweets(tweet),'negative') for tweet in negative_tweets]

    # print("training positive words ", positive_tweets)
    # print("training negative words ", negative_tweets)

    # use 80% of tweets for training
    fraction_pos = round(len(positive_tweets) * 0.8)
    fraction_neg = round(len(negative_tweets) * 0.8)

    # add all of the training tweets together and determine accuracy
    train_set = negative_tweets[:fraction_pos] + positive_tweets[:fraction_pos]
    test_set = negative_tweets[fraction_neg:] + positive_tweets[fraction_neg:]
    classifier = NaiveBayesClassifier.train(train_set)
    accuracy = nltk.classify.util.accuracy(classifier, test_set)

    return classifier, accuracy


def calculate_naughty(classifier, accuracy, user):
    user_tweets = api.user_timeline(screen_name=user, count=200)
    user_tweets = [tweet.text for tweet in user_tweets]
    user_tweets = clean_tweets(user_tweets)

    # classify the sentiment of each tweet
    rating = [classifier.classify(parse_tweets(tweet)) for tweet in user_tweets]

    # calculate the percentage of naughty or nice
    percent_naughty = rating.count('negative')/len(rating)
    if percent_naughty > .5:
        print(user, " is ", percent_naughty * 100, "% NAUGHTY with an accuracy of",
              accuracy)
    else:
        print(user, " is ", 100 - percent_naughty * 100, "% NICE with an accuracy of",
              accuracy)


def print_user_tweets(classifier, accuracy, user):
    user_tweets = api.user_timeline(screen_name=user, count=5)
    user_tweets = [tweet.text for tweet in user_tweets]
    user_tweets = clean_tweets(user_tweets)

    rating = [classifier.classify(parse_tweets(tweet)) for tweet in user_tweets]

    for tweet in user_tweets:
        print("rating = ", rating, " ", tweet)


# EXECUTE THE PROGRAM

# tweets = store_tweets('tweets.txt', tweets)
# tweets = clean_tweets(tweets)

pos_tweets, neg_tweets = sort_tweets(tweets)
classifier, accuracy = train_classifier(pos_tweets, neg_tweets)

# print("classifier", classifier)
# print("accuracy", accuracy)

# calculate_naughty(classifier, accuracy, 'muncho4_')
# calculate_naughty(classifier, accuracy, 'vt_medstudent')
calculate_naughty(classifier, accuracy, 'fabioyoohoo')

#print_user_tweets(classifier, accuracy, 'fabioyoohoo')
