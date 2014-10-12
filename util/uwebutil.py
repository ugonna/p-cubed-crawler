import logging
import urllib

def tidy_url(url):
	import urlparse
	
	if not urlparse.urlparse(url).scheme:
	   url = "http://" + url
	return url.encode('utf8')
	
def robot_allows_fetch(base_url, url_to_fetch):
	"""
	Checks the robots.txt in a base_url for if a url_to_fetch
	can be fetched
	
	Arguments:
	base_url -- the server's URL at which the robots.txt is located
	url_to_fetch -- the URL to check against in the robots.txt
	
	"""
	import robotparser
	
	# Validation
	tidy_url(base_url)
	tidy_url(url_to_fetch)
	
	rp = robotparser.RobotFileParser()
	rp.set_url(base_url + '/robots.txt') # Assuming document is at root
	rp.read()
	return rp.can_fetch('*', url_to_fetch)
	
def get_url_content(url, data={}, user_agent='Unknown'):
	"""
	Fetches content from a HTTP response for a HTTP request.
	Returns a tuple of the content, the content-type and the HTTP status code.
	
	Arguments:
	url -- the URL to GET
	data -- the data to URL encoding. In list of dict format [{a=b},{x=y}] (default={})
	user_agent -- the USER-AGENT to report to the serve (default='Unknown')
	
	"""
	from google.appengine.api import urlfetch
	
	url = tidy_url(url)
	header = {'User-Agent': user_agent};
	
	if data:
		url = '?'.join([url, urllib.urlencode(data)])
		
	# TODO: Check if robot_allows_fetch
	try:
		result = urlfetch.fetch(url=url, payload=None,\
										method=urlfetch.GET, headers=header)
		if result.status_code == 200:
			return result.content, result.headers['content-type'], result.status_code
		elif result.status_code == 404:
			logging.error("Page not found: %s" % url)
			return None, '', result.status_code
		else:
			return None, '', result.status_code
		# TODO: Return specific errors
			
	except urlfetch.Error as err:
		logging.error(err)
		return None, '', 500
