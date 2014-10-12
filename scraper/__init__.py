import urlparse, urllib, logging
import bot
from search import search


def recent_relevant_articles(keyword, from_date=None):
	recent_articles = bot.engadget_scraper(from_date)
	"""
	relevant_articles = [a for a in recent_articles
						 if search.is_keyword_in_post(keyword, a['post'])]
	"""
						 
	for a in recent_articles:
		if search.is_keyword_in_post(keyword, a['post']):
			yield a

