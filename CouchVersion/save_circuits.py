#!/usr/bin/env python

# Update decision relevance based on the presence of "17 U.S.C." 
# copyright code mention

import os, re
import couchdb
from BeautifulSoup import BeautifulSoup 

br = re.compile(r'<[bB][rR] *?/>')
cir = re.compile(r'(?:United States|U\.S\.) Court of Appeals(?:,| for the)? (.*?) Circuit', re.IGNORECASE)
cus = re.compile(r'(?:United States|U\.S\.) Court of (Customs and Patent) Appeals', re.IGNORECASE)
clm = re.compile(r'United States Court of (Claims)', re.IGNORECASE)
smp = re.compile(r'([A-Z][a-z]+) Circuit', re.IGNORECASE)

couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
# couch = couchdb.Server('http://127.0.0.1:5984')
db = couch['copyright_test']

courts_list = []
courts_list.append(('first', 'First'))
courts_list.append(('second', 'Second'))
courts_list.append(('third', 'Third'))
courts_list.append(('fourth', 'Fourth'))
courts_list.append(('fifth', 'Fifth'))
courts_list.append(('sixth', 'Sixth'))
courts_list.append(('seventh', 'Seventh'))
courts_list.append(('eighth', 'Eighth'))
courts_list.append(('ninth', 'Ninth'))
courts_list.append(('tenth', 'Tenth'))
courts_list.append(('eleventh', 'Eleventh'))
courts_list.append(('columbia', 'DC'))
courts_list.append(('federal', 'Federal'))
courts_list.append(('customs', 'Customs'))
courts_list.append(('claims', 'Claims'))


# At this point only decision docs in db, besides design doc
for ii,id in enumerate(db):
	if (ii % 200) == 0:
		print ii
	doc = db[id]
	if doc.has_key('type') and doc['type'] == 'decision' and doc.has_key('_attachments'):
		atts = doc['_attachments']
		hts = atts.keys()
		at = db.get_attachment(id, hts[0])
		s = at.read()
		
		soup = BeautifulSoup(s)
		
		court_found = False
		
		# Search first in the "court" class
		courts_html = br.sub(' ', str(" ".join([str(ss) for ss in soup.findAll("p", "court")])))
		
		# Standard
		court = cir.findall(courts_html)
		if len(court) > 0:
			court_found = True
		
		# Customs & Patent
		if not court_found:
			court = cus.findall(courts_html)
			if len(court) > 0:
				court_found = True
		
		# Claims
		if not court_found:
			court = clm.findall(courts_html)
			if len(court) > 0:
				court_found = True
		
		# try last some strange cases of split names in "court"
		if not court_found:
			court = smp.findall(courts_html)
			if len(court) > 0:
				court_found = True
		
		# last try in whole content and take first instance -- dangerous?
		if not court_found:
			court = cir.findall(doc['content'])
			if len(court) > 0:
				court_found = True
		
		if not court_found:
			court = cus.findall(doc['content'])
			if len(court) > 0:
				court_found = True
		
		# try last some strange cases of split names in whole content
		if not court_found:
			court = smp.findall(doc['content'])
			if len(court) > 0:
				court_found = True
		
		if court_found:
			# Substitute standard names and save doc
			name = court[0].lower()
			name_trans = False
			for stds in courts_list:
				if re.search(stds[0], name, re.IGNORECASE):
					name_trans = True
					doc['court'] = stds[1]
					db.save(doc)
					break
			if not name_trans:
				print id, name
		else:
			print '** Problem ** : ', id
					
		
