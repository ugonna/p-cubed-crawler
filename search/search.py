import difflib, re, string

def is_keyword_in_post(keyword, text):
	"""
	Searches for any occurence of a given keyword in a body of text.
	Returns no of occurences
	"""
	
	# Strip text of punctuations
	exclude = set(string.punctuation)
	text = ''.join(ch for ch in text if ch not in exclude)
	
	pattern = re.compile(r'\b({0})\b'.format(keyword), flags=re.IGNORECASE)
	occurences = [match for match in pattern.findall(text)]
		
	return len(occurences)
