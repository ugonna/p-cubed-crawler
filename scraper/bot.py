from bs4 import BeautifulSoup as bsoup
from util import udateutil, uwebutil
import datetime

import logging

sites =  ('http://engadget.com', 'http://theverge.com')
# Add as required. Check their privacy policy

USER_AGENT = 'ppp-bot/0.1 yourdomain.com/ppp'

#TODO: Use a more unique stop identifier than a date


def engadget_scraper(from_date=None):
	"""
	Extracts all articles from www.engadget.com after a specified date.
	Worked with the page format as of 2013-04-13.

	Returns a generator.

	Arguments:
	from_date -- the latest date to check against. Defaults to midnight
				 today UTC
	"""
	# Method loops till it meets an article that is on or before `from_date'

	ENG_MAIN_BODY_ID = 'body'
	ENG_POST_HEADER_CLASS = 'post-header'
	ENG_PAGINATION_ID = 'post-pagination'

	should_recur = True

	soup = _get_soup_from_url(sites[0])
	articles_html = soup.find('div', id='body').find_all('article')

	if from_date == None:
		# INFO: Returns as UTC on GAE, even though it's meant to be local time.
		now = datetime.datetime.today()
		# Get current UTC midnight
		from_date = udateutil.convert_naive_to_utc(
			datetime.datetime(now.year, now.month, now.day))
	else:
		from_date = udateutil.convert_naive_to_utc(from_date)

	while should_recur:
		# Extract all article links from the front page
		for article in articles_html:
			article_link = article.find('header', ENG_POST_HEADER_CLASS).\
				find('a', attrs={'itemprop':'url'})['href']

			article_date = udateutil.convert_string_to_date(article.\
				find('header', ENG_POST_HEADER_CLASS).find('span', 'time').\
				get_text())

			# Engadget dates are all in EST
			# TODO: Test this hypothesis on GAE prod server
			article_date = udateutil.convert_est_to_utc(article_date)

			if article_date <= from_date:
				logging.info('{0} is on or before to {1}'.\
					format(article_date, from_date))
				should_recur = False
				break

			article = {'url':article_link, 'created_at':article_date}

			# Get the article contents
			# TODO Handle 500 error
			article_soup = _get_soup_from_url(article['url'])

			article_body = article_soup.find('div', id='body').\
				find('div', 'post-body')
			if article_body:
			    article_text = article_body.get_text()
			else:
			    continue

			article['post'] = article_text.encode('utf-8')

			yield article

		if should_recur:
			# Move to the next page and get more articles
			# Gets the next page in relative form (/page/2)
			next_page_url = soup.find('ul', 'post-pagination').\
				find('li', 'older').find('a')['href']
			next_page_url = sites[0] + next_page_url
			# TODO Handle 500 error
			soup = _get_soup_from_url(next_page_url)
			articles_html = soup.find('div', id='body').find_all('article')
			continue
		else:
			break


def _get_soup_from_url(url):
	"""
	Returns a BeautifulSoup object using the HTML content from a url.

	Arguments:
	url -- A URL string from which to get the HTML document
	"""
	result = uwebutil.get_url_content(url, user_agent=USER_AGENT)
	content_type = result[1]
	result_code = result[-1]

	# If HTTP status code is 200
	if result_code == 200:
		html_content = result[0]
		return bsoup(html_content) # Holds the pages HTML content in bsoup format
	elif result_code == 500:
		# TODO Handle error
		logging.error("Error fetching {0}".format(url))
		return
