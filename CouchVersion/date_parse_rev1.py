#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os, re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

data_dir = '/Volumes/SciVis_LargeData/ArtMarkets/Subset2'

br = re.compile(r'<[bB][rR] *?/>', re.IGNORECASE)

date_re_dict = {}
date_re_dict['Numb'] = re.compile(r'[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
date_re_dict['Abbr'] = re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
date_re_dict['Full'] = re.compile(r'(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
date_re_dict['Bk Abbr'] = re.compile(r'[0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4}', re.IGNORECASE)
date_re_dict['Bk Full'] = re.compile(r'[0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4}', re.IGNORECASE)
date_re_dict['Decided Numb'] = re.compile(r'Decided:? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
date_re_dict['Decided Abbr'] = re.compile(r'Decided:? +((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
date_re_dict['Decided Full'] = re.compile(r'Decided:? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
date_re_dict['Decided Bk Abbr'] = re.compile(r'Decided:? +[0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4}', re.IGNORECASE)
date_re_dict['Decided Bk Full'] = re.compile(r'Decided:? +[0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4}', re.IGNORECASE)

def count_files(arg, dirname, files):
		
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			print '\n(', file, ')'
			
			f = open(fullpath,'r')
			s = f.read()
			f.close()
			soup = BeautifulSoup(s)
			
			# Check for a date field
			# If there is a date field but no date, need to check other places
			# If there are multiple dates, but not a decided date, may need to take non-Denied
			# From multiple date fields need to decide
			# Denied doesn't _always_ come right before the date "Rehearing Denied in No. 23325 April 25, 1955"
			#  (although most often yes)
			# There's one without decided, but with Argued and Filed...
			# and one with two decideds, the first in the head and the last in the footnotes...
			
			check_places = {}
			check_places['DATE'] = br.sub(' ', str(" ".join([str(ss) for ss in soup.findAll("p", "date")])))
			check_places['PRELIM'] = br.sub(' ', str(soup.find("div", {"class":"prelims"})))
			check_places['BODY'] = br.sub(' ', str(soup.body))
			
			date_found = False

			for (tag, place) in check_places.items():

				# Short-circuit places if a date has been found
				if date_found:
					continue

				print tag
				if tag == 'DATE':
					print place
					pass
				# Check all regular expressions
				for (k,v) in date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						print k, dates
						date_found = True
				

os.path.walk(data_dir, count_files, None)
