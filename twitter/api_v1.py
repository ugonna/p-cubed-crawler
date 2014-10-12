#!/usr/bin/python

'''Mini-library for access to Twitter API'''


from util.uwebutil import get_url_content

ERROR = 'error'

class TwitterSearchHandler(object):
	"""Handles Twitter search requests using API v1.1
	Only fetches tweets in English."""

	TWIT_SEARCH_URL = 'https://search.twitter.com/search.json'
	USER_AGENT = 'ppp-bot/0.1 yourdomain.com/ppp'
	_next_page_url_data = ''
	_since_id = 0
	_max_id = 0
	_fetch_next_pages = False

	def search(self, query='', with_entities='t', result_type='',
	    all_pages=False, since_id=None):
		"""Handles queries and other attributes for a Twitter search. Synchronous.
		"""
		self._fetch_next_pages = all_pages
		# If a previous page has been done before and we need more, get more
		if self._next_page_url_data and all_pages:

			search_result = self._twitter_search_url_get(self.TWIT_SEARCH_URL + \
			self._next_page_url_data)

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
		url_data['rpp'] = '100'
		if since_id:
		    self._since_id = since_id
		url_data['since_id'] = self._since_id
		url_data['include_entities'] = with_entities
		if not all_pages:
			return self._twitter_search_url_get(self.TWIT_SEARCH_URL, url_data)
		else:
			return self._twitter_search_url_get(self.TWIT_SEARCH_URL, url_data) + \
			self.search(all_pages=all_pages)
			# No need to pass the other parameters

	def reset_search(self):
		self._since_id=0

	def recent_self_id(self):
	    return self._since_id

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
			self._next_page_url_data = return_data.get('next_page')

			if self._next_page_url_data:
				self._since_id = return_data.get('since_id')
				self._max_id = return_data.get('max_id')
			else:
				# Cause it to fail
				# TODO: VERY improper, but will suffice for now
				self._next_page_url_data = 'fail'
			return return_data.get('results')
		else:
			# Assume error
			return return_data
