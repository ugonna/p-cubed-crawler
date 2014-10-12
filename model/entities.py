import datetime
from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class TrackedKeyWords(db.Expando):
	name = db.StringProperty(required=True)
	date_started = db.DateTimeProperty(auto_now_add=True, indexed=False)
	last_track_date = db.DateTimeProperty(indexed=False)
	since_id = db.IntegerProperty(indexed=False)
	
# ETL, bitches!
class KeyWordMention(polymodel.PolyModel):
	"""
	General tracked-keyword mentions
	"""
	date_time_mentioned = db.DateTimeProperty(required=True)
	sentiment = db.RatingProperty(indexed=False)


class SMKeyWordMention(KeyWordMention):
	"""
	Social media keyword mentions
	"""
	author = db.StringProperty(indexed=False)
	text = db.TextProperty(required=True, indexed=False)

	
class AKeyWordMention(KeyWordMention):
	"""
	Article, forum posts, blog keyword mentions
	"""
	url = db.LinkProperty(required=True, indexed=False)
