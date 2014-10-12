import datetime
import itertools
import pytz
import time

from email.utils import parsedate_tz, mktime_tz
from pytz import gae

def convert_rfc2822_to_date(rfc_2822_string):
	"""
	Converts a date string in RFC 2822 format to a UTC datetime object.
	This has to be written cos I can't simply do this:
	time.strptime(rfc_2822_string, '%a, %d %b %Y %H:%M:%S %Z')
	*sigh*
	"""
	time_tuple = parsedate_tz(rfc_2822_string) # (2009, 11, 16, 13, 32, 2, 0, 1, -1, 0)
	timestamp = mktime_tz(time_tuple)
	return datetime.datetime.fromtimestamp(timestamp)
	
	''' Useless, but kept as a lesson of what not to do.
		Both (above and below) achieve the same thing. Which is simpler?
	# Get the last element, the time zone
	time_zone_offset = time_tuple[-1] * 60 * 60
	
	timestamp = time.mktime(time_tuple[0:9]) + time.timezone - time_zone_offset
	return datetime.datetime.fromtimestamp(timestamp)'''

def convert_string_to_date(string):
	import dateutil.parser as parser
	
	return parser.parse(string)
	
def convert_naive_to_utc(naive_date):
	utc = pytz.utc
	return naive_date.replace(tzinfo=utc)
	
def convert_est_to_utc(eastern_date):
	utc = pytz.utc
	est = pytz.timezone('US/Eastern')
	eastern_date = eastern_date.replace(tzinfo=est)
	return eastern_date.astimezone(utc)
	

def group_dict_periodically(earliest_date, the_dict, date_key, grouping_period):
	"""
	DEPRECATED - See group_periodically
	
	Groups a given dictionary into collections based on time period.
	Returns a list of tuples. Format:
	
	[(group_key_1, [{'dict1':dict1},{'dict2':dict2}...]),
	 (group_key_2, [{'dict3':dict3},{'dict4':dict4}...]),...]
	 
	Arguments:
	earliest_date -- the earliest date in the list
	the_dict -- the dict to group
	date_key -- the key to access the dates in the dict with
	grouping_period -- grouping period to group by. One of date.per_minute, 
					   date.hourly, date.six_hourly or date.daily
	"""
	return [(key, list(grp)) for key, grp
				in itertools.groupby(the_dict,
				key=lambda tweet:grouping_period(tweet[date_key], earliest_date))]
				
def group_periodically(earliest_date, the_dict, date_key, grouping_period):
	"""
	DEPRECATED - See group_periodically
	
	Groups a given dictionary into collections based on time period.
	Returns a list of tuples. Format:
	
	[(period_start_time, num_in_period), (period_start_time_2, num_in_period)
	(period_start_time_3, num_in_period),...]
	
	`period_start_time` is ms since Unix epoch
	 
	Arguments:
	earliest_date -- the earliest date in the list
	the_dict -- the dict to group
	date_key -- the key to access the dates in the dict with
	grouping_period -- grouping period to group by. One of date.per_minute, 
					   date.hourly, date.six_hourly or date.daily
	"""
	return [_pack(key, list(grp), date_key) for key, grp
				in itertools.groupby(the_dict,
				key=lambda tweet:grouping_period(tweet[date_key], earliest_date))]

def _pack(key, group, date_key):
	return time.mktime(group[0][date_key].timetuple()) * 1000, len(group)

def per_minute(date, start_date):
	return ((date - start_date).total_seconds() // 60) // 1
	
def hourly(date, start_date):
	return ((date - start_date).total_seconds() // 3600) // 1

def six_hourly(date, start_date):
	return ((date - start_date).total_seconds() // 3600) // 6
	
def daily(date, start_date):
	return (date - start_date).days
