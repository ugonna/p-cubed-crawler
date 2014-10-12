import datetime
import scraper
import webapp2
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext import deferred
from model import entities
from twitter import api_v1
from util.udateutil import convert_rfc2822_to_date as convert_date

class FetchWebPagesTaskHandler(webapp2.RequestHandler):

	def get(self):
		query = entities.TrackedKeyWords.all()
		
		countdown = 300
		for idx, kw in enumerate(query.run(batch_size=5)):
			deferred.defer(
				crawl_web, kw.key(), kw.name, kw.last_track_date,
				_queue="webcrawl", _countdown=idx*countdown)
		

class FetchSocialMediaTaskHandler(webapp2.RequestHandler):

	def get(self):
		query = entities.TrackedKeyWords.all()
		
		countdown = 120
		for idx, kw in enumerate(query.run(batch_size=5)):
			deferred.defer(
				crawl_sm, kw.key(), kw.name, kw.since_id,
				_queue="socialcrawl", _countdown=idx*countdown)


def crawl_web(kw_key, kw_name, kw_last_tracked_date):
	recent_articles = scraper.recent_relevant_articles(kw_name, kw_last_tracked_date)

	print kw_last_tracked_date
	
	for article in recent_articles:
		kw_mention = entities.AKeyWordMention(
			parent=kw_key, url=article['url'],
			date_time_mentioned=article['created_at'])
		    
		kw_mention.put()
    
	# Is VERY liable to miss an article posted between the seconds
	# the last article was retrieved/saved and now
	print datetime.datetime.now()
	tkw = entities.TrackedKeyWords.get(kw_key)
	tkw.last_track_date = datetime.datetime.now() # UTC
	tkw.put()


def crawl_sm(kw_key, kw_name, kw_since_id):
	# TODO Date of last crawl
	
	# Get relevant SM posts
	searchHandle = api_v1.TwitterSearchHandler()
	recent_tweets = searchHandle.search(query=kw_name, all_pages=True,\
	    since_id=kw_since_id)

	@db.transactional
	def store_tweet_txn(tweets):
		for tweet in tweets:
			kw_mention = entities.SMKeyWordMention(parent=kw_key,\
			 									   from_user=tweet['from_user'],\
			 									   text=tweet['text'],\
			 									   date_time_mentioned=\
			 									   convert_date(tweet['created_at']))
			kw_mention.put()
				
	store_tweet_txn(recent_tweets)
	tkw = entities.TrackedKeyWords.get(kw_key)
	tkw.since_id = searchHandle.recent_self_id()
	tkw.put()

app = webapp2.WSGIApplication([('/tasks/webcrawler', FetchWebPagesTaskHandler),
							  ('/tasks/socialcrawler', FetchSocialMediaTaskHandler)],
                              debug=True)
