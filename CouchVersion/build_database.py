#!/usr/bin/env python

# Do date parsing and build initial copyright_test CouchDB database

import os, re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag
from uuid import uuid4
import couchdb
import string
from datetime import datetime
from html2text import html2text

data_dir = '/Volumes/SciVis_LargeData/ArtMarkets/Subset2'
# data_dir = '/Users/emonson/Data/ArtMarkets/Subset2'
db_name = 'copyright_test'

nondate_tag_list = ['court', 'case_cite', 'parties', 'docket']

bad_copyright = re.compile('copyright material omitted|copyrighted material omitted', re.IGNORECASE)
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
dec_date_re_dict['Numb'] = re.compile(r'Decided(?: and filed)?:? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
dec_date_re_dict['Abbr'] = re.compile(r'Decided(?: and filed)?:? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
dec_date_re_dict['Full'] = re.compile(r'Decided(?: and filed)?:? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
dec_date_re_dict['Abbr_Bk'] = re.compile(r'Decided(?: and filed)?:? +([0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4})', re.IGNORECASE)
dec_date_re_dict['Full_Bk'] = re.compile(r'Decided(?: and filed)?:? +([0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4})', re.IGNORECASE)

den_date_re_dict = {}
den_date_re_dict['Numb'] = re.compile(r'(?:Denied|Declined|Denial of Rehearing):? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
den_date_re_dict['Abbr'] = re.compile(r'(?:Denied|Declined|Denial of Rehearing):? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
den_date_re_dict['Full'] = re.compile(r'(?:Denied|Declined|Denial of Rehearing):? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
den_date_re_dict['Abbr_Bk'] = re.compile(r'(?:Denied|Declined|Denial of Rehearing):? +([0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4})', re.IGNORECASE)
den_date_re_dict['Full_Bk'] = re.compile(r'(?:Denied|Declined|Denial of Rehearing):? +([0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4})', re.IGNORECASE)

as_date_re_dict = {}
as_date_re_dict['Numb'] = re.compile(r'(?:Argued|Argued and Submitted|Submitted)(?::| on| En Banc)? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
as_date_re_dict['Abbr'] = re.compile(r'(?:Argued|Argued and Submitted|Submitted)(?::| on| En Banc)? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
as_date_re_dict['Full'] = re.compile(r'(?:Argued|Argued and Submitted|Submitted)(?::| on| En Banc)? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
as_date_re_dict['Abbr_Bk'] = re.compile(r'(?:Argued|Argued and Submitted|Submitted)(?::| on| En Banc)? +([0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4})', re.IGNORECASE)
as_date_re_dict['Full_Bk'] = re.compile(r'(?:Argued|Argued and Submitted|Submitted)(?::| on| En Banc)? +([0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4})', re.IGNORECASE)

fil_date_re_dict = {}
fil_date_re_dict['Numb'] = re.compile(r'(?:Filed):? +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
fil_date_re_dict['Abbr'] = re.compile(r'(?:Filed):? +((?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
fil_date_re_dict['Full'] = re.compile(r'(?:Filed):? +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
fil_date_re_dict['Abbr_Bk'] = re.compile(r'(?:Filed):? +([0-9][0-9]? +?(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\. +[0-9]{4})', re.IGNORECASE)
fil_date_re_dict['Full_Bk'] = re.compile(r'(?:Filed):? +([0-9][0-9]? +?(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9]{4})', re.IGNORECASE)

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

# couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
couch = couchdb.Server('http://127.0.0.1:5984')

# For now, always recreate database...
# if db_name in couch:
# 	couch.delete(db_name)
# 
# db = couch.create(db_name)
# 
# test1 = couch['test2']
# test1_design = test1['_design/test1']
# del test1_design['_rev']
# db.save(test1_design)

# At this point creating the database with CouchApp, including
# adding the design docs, so just load the existing database
db = couch['copyright_test']

count = 0

def count_files(arg, dirname, files):
	global count, db
	
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			
			if (count % 10) == 0:
				print count
			count += 1
			print_it = False

			f = open(fullpath,'r')
			s = f.read()
			f.close()
			
			# Replace all breaks, bolds and italics before doing soup
			s = br.sub(' ', s)
			s = bi.sub('', s)
			s = bo.sub('', s)
			s = ii.sub('', s)
			s = io.sub('', s)
			s = bad_copyright.sub('', s)
			
			soup = BeautifulSoup(s)
			
			# Replace all footnote links with [-n-]
			aa = soup.findAll('a','footnote')
			for ll in aa:
				ll.replaceWith('[-' + ll.string + '-]')
			
			# Take out all paragraph numbering
			sp = soup.findAll('span','num')
			for ll in sp:
				ll.extract()
			
			# Take off footer
			ff = soup.find('div',{'id':'footer'})
			if ff is not None:
				ff.extract()
			
			check_places = {}
			check_places['DATE'] = br.sub(' ', str(" ".join([str(ss) for ss in soup.findAll("p", "date")])))
			if len(check_places['DATE']) == 0:
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
							plain_dates.append([k, date])

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
							decided_dates.append([k, date])

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
							denied_dates.append([k, date])
			
			# Check all argued and/or submitted dates
			date_found = False
			as_dates = []
			for (tag, place) in check_places.items():
				# Short-circuit places if a date has been found
				if date_found:
					continue
				for (k,v) in as_date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						date_found = True
						for date in dates:
							as_dates.append([k, date])
			
			# Check all filed dates
			date_found = False
			fil_dates = []
			for (tag, place) in check_places.items():
				# Short-circuit places if a date has been found
				if date_found:
					continue
				for (k,v) in fil_date_re_dict.items():
					dates = v.findall(place)
					if len(dates) > 0:
						date_found = True
						for date in dates:
							fil_dates.append([k, date])
			
# 			if (len(decided_dates) != 1) and (len(plain_dates) > (len(denied_dates)+1)) and not (len(plain_dates) == (len(as_dates)+len(fil_dates))): # (len(decided_dates) > 1) or (len(plain_dates) == 0) or (len(denied_dates) > (1+len(plain_dates))) or (len(plain_dates) > 1 and len(decided_dates) == 0 and len(denied_dates) == 0):
# 				print "(", file, ")"
# 				print check_places['DATE']
# 				print "Plain:", plain_dates
# 				print "Decid:", decided_dates
# 				print "Denyd:", denied_dates
# 				print "ArSub:", as_dates
# 				print "Filed:", fil_dates
# 				print

			date_found = False
			date = None
			
			# Date logic... Short circuit process after each (don't let run through)
			
			# If only one plain date -> that's the date
			if len(plain_dates) == 1:
				date = plain_dates[0]
				date_found = True
				
			# If one decided date -> that's the date
			if not date_found:
				if len(decided_dates) == 1:
					date = decided_dates[0]
					date_found = True
			
			# If more than one decided date -> problem (leave date == None)
			if not date_found:
				if len(decided_dates) > 1:
					date_found = True
			
			# If len(denied_dates) > 0 and == len(plain_dates)-1, find non-denied plain date -> that's the date
			if not date_found:
				if (len(denied_dates) > 0) and (len(plain_dates) == len(denied_dates)+1):
					pln = set([(k,v) for [k,v] in plain_dates])
					den = set([(k,v) for [k,v] in denied_dates])
					date_set = pln.difference(den)
					date = list(date_set.pop())
					date_found = True
				
			# if (len(fil_dates) == 1) and (len(plain_dates) == (len(as_dates)+len(fil_dates))) -> choose filed date
			if not date_found:
				if (len(fil_dates) == 1) and (len(plain_dates) == (len(as_dates)+len(fil_dates))):
					date = fil_dates[0]
					date_found = True
			
			# Replace abbreviations
			if date_found and (not date is None) and date[0].startswith('Abbr'):
				for mo in abbr_list:
					if date[1].find(mo[0]) >= 0:
						date[1] = date[1].replace(mo[0],mo[1])
						date[0] = date[0].replace('Abbr','Full')							
						break

			final_date_string = None
			
			# Replace date with YYYY-MM-DD format
			if date_found and (date is not None):
				if date[0].startswith('Full'):
					if date[0].endswith('_Bk'):
						tt = datetime.strptime(date[1], "%d %B %Y")
						final_date_string = tt.strftime('%Y-%m-%d')
					else:
						tt = datetime.strptime(date[1], "%B %d, %Y")
						final_date_string = tt.strftime('%Y-%m-%d')
				elif date[0].startswith('Numb'):
					# Need to force the right range on years: 00 - 68 show up as 2000-2068...
					# We know our year range is 1949 to 2007
					split_date = date[1].split('/')
					year_int = int(split_date[2])
					if year_int < 20:
						split_date[2] = str(2000 + year_int)
					else:
						split_date[2] = str(1900 + year_int)
					tt = datetime.strptime('/'.join(split_date), "%m/%d/%Y")
					final_date_string = tt.strftime('%Y-%m-%d')
				else:
					final_date_string = 'YYYY-YY-YY'
			
			if (not date_found) or (date is None):
				final_date_string = 'XXXX-XX-XX'
				print "(", file, ")"
				print check_places['DATE']

			# Create the document ID
			id = uuid4().hex
			doc = {'_id': id, 'type': 'decision', 'relevant': True}
			doc['date'] = final_date_string
			doc['content'] = html2text(str(soup))
			db.save(doc)
			
			# Reload to do attachment
			doc = db[id]
			db.put_attachment(doc, s, file)

os.path.walk(data_dir, count_files, None)

# {u'court': 3228, 
#  u'center': 583, 
#  u'case_cite': 5130, 
#  u'blank_attr': 64773, 
#  u'parties': 3268, 
#  u'date': 3840, 
#  u'indent': 154069, 
#  u'docket': 3566}
