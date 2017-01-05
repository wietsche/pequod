#!/usr/bin/python
import sys
import boto.sqs
import os
from datetime import datetime
import twitter

AWS_KEY = 'AKIAITC6LDENNQBKSW3A'
AWS_SECRET = '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' 

TWITTER_KEY = 'p3iv6FH7pL7hyOUNh3yygjBCU'
TWITTER_SECRET = 'dJDzSke1Dy7IrnN6FzWvx53JJj6A7v5mVFSCCHwuf24ha3Y4Wz'
ACCESS_TOKEN = '3953960675-6zIeSHd7LbYuzJF5y679oQ25cX9pxvAvbd1q5mV'
ACCESS_TOKEN_SECRET = 'hlJKpdp4mscdasu9jiNhSQ63qEY7aUXMU7eFWDOC86YYz'

api = twitter.Api(consumer_key=TWITTER_KEY,
        consumer_secret=TWITTER_SECRET,
        access_token_key=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET)

conn = boto.sqs.connect_to_region("us-west-2")
#print api.VerifyCredentials()

twitq = conn.get_queue('twitter')
archq = conn.get_queue('twitter_arch') 
tweets = twitq.get_messages()
for m in tweets:
    text  = m.get_body()
    text = text[:-3] #remove seconds
    print text
    #status = api.PostUpdate(text)
    twitq.delete_message(m)
    archq.write(m)
    #print "Tweeted and archived: " + status.text

