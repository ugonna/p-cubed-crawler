import cgi
import datetime
import jinja2
import json
import os
import webapp2

from google.appengine.ext import db
from model import entities
from util.udateutil import convert_rfc2822_to_date as convert_date
from util.udateutil import group_periodically
from util.udateutil import daily
from util.udateutil import hourly


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
		
		
class HomePageHandler(webapp2.RequestHandler):

	def get(self):

		tkw_query = entities.TrackedKeyWords.all()
		all_tkw = [kw for kw in tkw_query.run(limit=10)]
		
		template_values = {
			'tracked_kw': all_tkw,
		}
		
		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

		
class ViewPageHandler(webapp2.RequestHandler):

	def get(self):
		
		product_id = int(self.request.get('id'))
		product = entities.TrackedKeyWords.get_by_id(product_id)
		
		template_values = {
			'product': product,
		}
		
		template = jinja_environment.get_template('templates/view.html')
		self.response.out.write(template.render(template_values))


class AJAXHandler(webapp2.RequestHandler):

    """ Handles our AJAX requests"""
    def get(self):
		action = self.request.get('action')
		
		if action == 'getstats':
			prod_key = db.Key(self.request.get('key'))
			sm_prod_cursor = self.request.get('sm_cursor')
			a_prod_cursor = self.request.get('a_cursor')
			
			# Get Social media key word (sm kw) mentions
			sm_kwm_query = entities.SMKeyWordMention.all()
			sm_kwm_query.ancestor(prod_key)
			sm_kwm_query.order('date_time_mentioned')
			if sm_prod_cursor:
				sm_kwm_query.with_cursor(start_cursor=sm_prod_cursor)
			
			sm_kw_mentions = [{ 'date':kwm.date_time_mentioned,
				'sent':kwm.sentiment }
				for kwm in sm_kwm_query.run(limit=500)]
				
			sm_kw_groups = []
			if sm_kw_mentions:
				sm_kw_groups = group_periodically(sm_kw_mentions[0]['date'],\
					sm_kw_mentions, u'date', hourly)
			
			# Get Article mentions
			a_kwm_query = entities.AKeyWordMention.all()
			a_kwm_query.ancestor(prod_key)
			a_kwm_query.order('date_time_mentioned')
			if a_prod_cursor:
				a_kwm_query.with_cursor(start_cursor=a_prod_cursor)
			
			a_kw_mentions = [{ 'date':kwm.date_time_mentioned,
				'sent':kwm.sentiment }
				for kwm in a_kwm_query.run(limit=50)]
			
			a_kw_groups = []
			if a_kw_mentions:
				a_kw_groups = group_periodically(a_kw_mentions[0]['date'],\
					a_kw_mentions, u'date', daily)
				
			# Return the data
			ret_data = { 'sm_mentions' : sm_kw_groups,\
				'a_mentions' : a_kw_groups}
			ret_data['sm_cursor'] = sm_kwm_query.cursor()
			ret_data['a_cursor'] = a_kwm_query.cursor()

			ret_data_json = json.dumps(ret_data, sort_keys=True,\
				indent=4)

			self.response.headers['Content-Type'] = 'application/json'
			self.response.out.write(ret_data_json)
			
			
    def post(self):
		""" 
		Initializes tracking of a particluar keyword 
		"""
		action = self.request.get('action')
		if action == 'start':
			keyword = self.request.get('keyword')
			query = entities.TrackedKeyWords.all()
			query.filter("name =", keyword)

		if keyword and (query.get() is None) and len(keyword) < 16:
			# Store keyword for later tracking and start tracking
			tracked_keyword = entities.TrackedKeyWords(name=keyword)
			tracked_keyword.put()

		self.redirect('/')

# TODO: Remove
def initialize_datastore():
	"""
	Temporary method for initializing datastore with test data
	"""
	
	tracked_keyword = entities.TrackedKeyWords(name='iPhone')
	tracked_keyword.put()
	
	tracked_keyword = entities.TrackedKeyWords(name='HTC One')
	tracked_keyword.put()
	
	tracked_keyword = entities.TrackedKeyWords(name='Galaxy S IV')
	tracked_keyword.put()

		
app = webapp2.WSGIApplication([
	('/', HomePageHandler),
	('/view', ViewPageHandler),
	('/ajax', AJAXHandler)], debug=True)
