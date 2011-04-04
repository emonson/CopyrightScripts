#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os, re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from uuid import uuid4
import couchdb

data_dir = '/Volumes/SciVis_LargeData/ArtMarkets/Subset2'
# data_dir = '/Users/emonson/Data/ArtMarkets/Subset2'
db_name = 'copyright_test'

nondate_tag_list = ['court', 'case_cite', 'parties', 'docket']

br = re.compile(r'<[bB][rR] *?/>')
bi = re.compile(r'<[bB]>')
bo = re.compile(r'</[bB]>')
ii = re.compile(r'<[iI]>')
io = re.compile(r'</[iI]>')

date_re_dict = {}
date_re_dict['Numb'] = re.compile(r'[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
date_re_dict['Abbr'] = re.compile(r'(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
date_re_dict['Full'] = re.compile(r'(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
date_re_dict['Abbr_Bk'] = re.compile(r'[0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4}', re.IGNORECASE)
date_re_dict['Full_Bk'] = re.compile(r'[0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4}', re.IGNORECASE)

dec_date_re_dict = {}
dec_date_re_dict['Numb'] = re.compile(r'Decided:? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
dec_date_re_dict['Abbr'] = re.compile(r'Decided:? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
dec_date_re_dict['Full'] = re.compile(r'Decided:? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
dec_date_re_dict['Abbr_Bk'] = re.compile(r'Decided:? +[0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4}', re.IGNORECASE)
dec_date_re_dict['Full_Bk'] = re.compile(r'Decided:? +[0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4}', re.IGNORECASE)

den_date_re_dict = {}
den_date_re_dict['Numb'] = re.compile(r'Denied:? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
den_date_re_dict['Abbr'] = re.compile(r'Denied:? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
den_date_re_dict['Full'] = re.compile(r'Denied:? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
den_date_re_dict['Abbr_Bk'] = re.compile(r'Denied:? +[0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4}', re.IGNORECASE)
den_date_re_dict['Full_Bk'] = re.compile(r'Denied:? +[0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4}', re.IGNORECASE)

abbr_list = []
abbr_list.append(('Jan.', 'January'))
abbr_list.append(('Jan', 'January'))
abbr_list.append(('Feb.', 'February'))
abbr_list.append(('Feb', 'February'))
abbr_list.append(('Mar.', 'March'))
abbr_list.append(('Mar', 'March'))
abbr_list.append(('Apr.', 'April'))
abbr_list.append(('Apr', 'April'))
abbr_list.append(('Jun.', 'June'))
abbr_list.append(('Jul', 'July'))
abbr_list.append(('Aug.', 'August'))
abbr_list.append(('Aug', 'August'))
abbr_list.append(('Sept.', 'September'))
abbr_list.append(('Sept', 'September'))
abbr_list.append(('Sep.', 'September'))
abbr_list.append(('Sep', 'September'))
abbr_list.append(('Oct.', 'October'))
abbr_list.append(('Oct', 'October'))
abbr_list.append(('Nov.', 'November'))
abbr_list.append(('Nov', 'November'))
abbr_list.append(('Dec.', 'December'))
abbr_list.append(('Dec', 'December'))

couch = couchdb.Server('http://127.0.0.1:5984')

# For now, always recreate database...
if db_name in couch:
	couch.delete(db_name)

db = couch.create(db_name)

count = 0

def count_files(arg, dirname, files):
	global count, db
	
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			
			if (count % 100) == 0:
				print count
			count += 1

			f = open(fullpath,'r')
			s = f.read()
			f.close()
			soup = BeautifulSoup(s)
			
			check_places = {}
			check_places['DATE'] = br.sub(' ', str(" ".join([str(ss) for ss in soup.findAll("p", "date")])))
			check_places['PRELIM'] = br.sub(' ', str(soup.find("div", {"class":"prelims"})))
			check_places['BODY'] = br.sub(' ', str(soup.body))

			# Check all plain dates
			date_found = False
			plain_dates = []
			for (tag, place) in check_places.items():
				# Short-circuit places if a date has been found
				if date_found:
					continue
				for (k,v) in date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						date_found = True
						for date in dates:
							plain_dates.append((k, date))

			# Check all decided dates
			date_found = False
			decided_dates = []
			for (tag, place) in check_places.items():
				# Short-circuit places if a date has been found
				if date_found:
					continue
				for (k,v) in dec_date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						date_found = True
						for date in dates:
							decided_dates.append((k, date))

			# Check all denied dates
			date_found = False
			denied_dates = []
			for (tag, place) in check_places.items():
				# Short-circuit places if a date has been found
				if date_found:
					continue
				for (k,v) in den_date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						date_found = True
						for date in dates:
							denied_dates.append((k, date))
			
			if len(decided_dates) > 1 or len(denied_dates) > 1 or (len(plain_dates) > 1 and len(decided_dates) == 0 and len(denied_dates) == 0):
				print "(", file, ")"
				print check_places['DATE']
				print "Plain:", plain_dates
				print "Decid:", decided_dates
				print "Denyd:", denied_dates
				print


# 			id = uuid4().hex
# 			doc = {'_id': id, 'type': 'decision', 'relevant': True}
# 			
# 			# Reload to do attachment
# 			doc = db[id]
# 			db.put_attachment(doc, s, file)

os.path.walk(data_dir, count_files, None)

# {u'court': 3228, 
#  u'center': 583, 
#  u'case_cite': 5130, 
#  u'blank_attr': 64773, 
#  u'parties': 3268, 
#  u'date': 3840, 
#  u'indent': 154069, 
#  u'docket': 3566}
