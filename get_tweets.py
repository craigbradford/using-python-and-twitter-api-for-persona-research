import re
import csv

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

# make variables for the two Alchemi APIs I want to use
ConceptsAPI = "http://gateway-a.watsonplatform.net/calls/url/URLGetRankedConcepts?apikey=" + watson_api_key + "&url="

usernames = open('usernames.txt', 'r+') # make a variable for the Twitter usernames file by reading the text file usernames.txt
usernames = usernames.read().splitlines() # create a variable named usernames which is the usernames split by line. 


def CountDomains():
    for name in usernames: #for all the usernames in the usernames file...

        public_tweets = api.user_timeline(name, count=10) #create a variable named public_tweets which is the users last n tweets
        
        for tweet in public_tweets: #for every tweet in the public_tweets list...
        
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet.text) # use regex to find the links in the tweet body
            
            for url in urls: # for every url in the list of urls that the regex found
                try:
                    link = requests.get(url, allow_redirects=True).url  # request each link using the requests library and follow redirects to the end. This stops links like t.co showing up in the results
                    links.append(link) #put all of the urls into the list named links
                    domain = get_tld(link) #use the get_tld function from the tld library to turn urls into domains
                    domains.append(domain)#append the domain to the domains list that was created at the start
                    
                except Exception, e:
                    print link
    
    for link in links: # for each of the urls in the urls list that was created above...
        apiurl = ConceptsAPI+link # create a new url by concatenating the concepts API base url (defined at the start) to the link we want to get the concepts for
        
        r =  requests.get(apiurl) # create a variable named r which is the content from the API request

        doc = ElementTree.fromstring(r.text) # use the ElementTree function from the xml library to create a new variable named doc from the xml returned in the API call
        
        for tag in doc.findall('.//text'): # find all the <text> tags in the xml that is returned and assign the name tag. The <text> tag is the concept text that we want to keep a list of.
            tags.append(tag.text)

#   print "The top domains these people read are:"
#   print Counter(domains)
#   print "The topics this person is interested in are:"
#   print Counter(tags)
    with open("persona.csv", "a") as personas:
        personaswriter = csv.writer(personas)
        for domain in domains:
            personaswriter.writerow([domains,tags])
        personas.close()
        

CountDomains()
    
      