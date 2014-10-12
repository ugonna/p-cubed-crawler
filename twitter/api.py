#!/usr/bin/python

'''Mini-library for access to Twitter API v1.1 (incomplete)'''

import oauth2
from util import get_url_content

ERROR = 'errors'
CONSUMER_KEY = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET = 'YOUR_CONSUMER_SECRET'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTH_TOKEN_URL = 'https://api.twitter.com/oauth/authorize'

class TwitterSearchHandler(object):
	"""Handles Twitter search requests using API v1.1
	Only fetches tweets in English."""

	TWIT_SEARCH_URL = 'https://api.twitter.com/1.1/search/tweets.json'
	USER_AGENT = 'ppp-bot/0.1 yourdomain.com/ppp'
	next_page_url_data = ''
	since_id = 0
	max_id = 0
	fetch_next_pages = False

	def search(self, query='', with_entities='true', result_type='', all_pages=False):
		"""Handles queries and other attributes for a Twitter search. Synchronous.
		"""
		self.fetch_next_pages = all_pages
		# If a previous page has been done before and we need more, get more

		if self.next_page_url_data and all_pages:

			search_result = self._twitter_search_url_get(self.TWIT_SEARCH_URL + \
			self.next_page_url_data)

			# If the next page has any results...
			if search_result and ERROR not in search_result:
				#... return this result plus a recursive call to this method
				return search_result + self.search(all_pages=all_pages)
			else:
				return []

		# Create a query
		url_data = {}
		url_data['q'] = query
		url_data['lang'] = 'en'
		url_data['result_type'] = result_type if result_type=='mixed' else 'recent'
		url_data['count'] = '100'
		url_data['since_id'] = self.since_id
		url_data['include_entities'] = with_entities
		if not all_pages:
			return self._twitter_search_url_get(self.TWIT_SEARCH_URL, url_data)
		else:
			return self._twitter_search_url_get(self.TWIT_SEARCH_URL, url_data) + \
			self.search(all_pages=all_pages)
			# No need to pass the other parameters

	def reset_search(self):
		self.since_id=0

	def _twitter_search_url_get(self, url, data={}):
		"""
		Fetches and returns content from Twitter search results.
		Content is returned as []s and {}s
		"""

		result = get_url_content(url, data, self.USER_AGENT)
		result_content = result[0]
		result_code = result[-1]

		if result_code == 200:
			return self._parse_twitter_json_response(result_content)
		elif result_code == 403:
			return {ERROR: "Please check your query"}
		elif result_code == 420:
			return {ERROR: "Please try again later"}
		else:
			return {ERROR: "Server can't fulfill request yet. Error %d" % result_code}

	def _parse_twitter_json_response(self, response):
		"""Parses a JSON response from a Twitter search request.
		Updates the since_id"""
		import json
		return_data = json.loads(response)

		if ERROR not in return_data:
			# If there is a next page, store it
			# Using .get() to return None if key not present
			result_metadata = return_data.get('search_metadata')
			self.next_page_url_data = result_metadata.get('next_results')

			if self.next_page_url_data:
				self.since_id = result_metadata.get('since_id')
				print since_id
				self.max_id = result_metadata.get('max_id')
			else:
				# Cause it to fail
				# TODO: VERY improper, but will suffice for now
				self.next_page_url_data = 'fail'
			return return_data.get('statuses')
		else:
			# Assume error
			return return_data
