import re
import csv
import datetime
import requests
import tweepy
from xml.etree import ElementTree
from collections import Counter
from tweepy import API
from tweepy import OAuthHandler
from tld import get_tld

from api_keys import *


# Twitter auth
auth = tweepy.OAuthHandler(twitter_ckey, twitter_csecret)
auth.set_access_token(twitter_atoken, twitter_asecret)
api = tweepy.API(auth)

# create some empty lists
links = []
domains = []
firstpass = []
topics = []
tags = []

# make variables for the two Alchemy APIs I want to use
ConceptsAPI = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedConcepts?apikey=" + watson_api_key + "&url="

# make a variable for the Twitter usernames file by reading the text
# file usernames.txt
usernames = open('usernames.txt', 'r+')
# create a variable named usernames which is the usernames split by line.
usernames = usernames.read().splitlines()


def CountDomains(usernames):

    print "Starting tweet collection..."
    print str(len(usernames)) + " usernames.\n"

    # for all the usernames in the usernames file...
    for name in usernames:
        try:
            # create a variable named public_tweets
            public_tweets = api.user_timeline(name, count=20)
        except:
            print "private profile"
            continue
        # for every tweet in the public_tweets list...
        for tweet in public_tweets:

            # use regex to find the links in the tweet body
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet.text)

            # for every url in the list of urls that the regex found
            for url in urls:
                try:
                    # request each link using the requests library
                    # follow redirects.
                    link = requests.get(url, allow_redirects=True).url
                    # put all of the urls into the list named links
                    links.append(link)
                    # use the get_tld function from the tld library
                    domain = get_tld(link)
                    # append the domain to the domains list
                    domains.append(domain)
                except:
                    pass

        print "\tFinished: " + name

    print "\nStarting Alchemy analysis of links..."
    print str(len(links)) + " links.\n"

    # for each of the urls in the urls list that was created above...
    for link in links:
        # create a new url by concatenating the concepts API base url
        # (defined at the start) to the link we want to get the concepts for
        apiurl = ConceptsAPI+link

        # create a variable named r which is the content from the API request
        r = requests.get(apiurl)

        # use the ElementTree function from the xml library to create
        # a new variable named doc from the xml returned in the API call
        doc = ElementTree.fromstring(r.text)

        # find all the <text> tags in the xml and assign the name tag.
        # The <text> tag is the concept text that we want to keep a list of.
        for tag in doc.findall('.//text'):
            tags.append(tag.text)
        print "\tFinished: " + link

    print "\nDone. :)"

    today = datetime.datetime.now()
    postfix = today.strftime('%Y-%m-%d-%H-%M')

    with open("domains_" + postfix + ".csv", "a") as personas:
        personaswriter = csv.writer(personas)
        for domain, count in dict(Counter(domains)).items():
            personaswriter.writerow([domain, count])
        personas.close()

    with open("concepts_" + postfix + ".csv", "a") as concepts:
        conceptswriter = csv.writer(concepts)
        for tag, count in dict(Counter(tags)).items():
            conceptswriter.writerow([tag, count])
        concepts.close()

CountDomains(usernames)
