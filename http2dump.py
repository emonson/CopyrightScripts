#!/usr/bin/env python

# Grab Google Scholar case decisions from search results
# and dump files into GridFS

import sys
from BeautifulSoup import BeautifulSoup
import re
import time
from pymongo import Connection
import gridfs
import random
import urllib
import httplib2
# import urlparse as UP

# Make a connection to Mongo.
try:
    # db_conn = Connection("localhost", 27017)
    db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    # sys.stdout.flush()
    sys.exit(1)

# Drop database for now!!
# db_conn.drop_database('fashion_ip')
db = db_conn['fashion_ip']
fs = gridfs.GridFS(db)

host = 'http://scholar.google.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0.1) Gecko/20100101 Firefox/8.0.1'}

http = httplib2.Http()
count = 0

init_url = host
response, content = http.request(init_url, 'GET', headers=headers)
print "Response:\n", response

if response['status'] in ['302', '503']:
	print "REDIRECT!!"
	sys.exit(1)
			
headers['Cookie'] = response['set-cookie']
print "\nNew Headers:\n", headers

for year in range(2007,2013):
	
	print "\n** YEAR:", year
	# sys.stdout.flush()
	
	# all courts, one year
	query_dict = {'as_sdt': ['6,34'],
	 'as_vis': ['0'],
	 'btnG': ['Search'],
	 'hl': ['en'],
	 'num': ['10'],
	 'as_ylo': [str(year)],
	 'as_yhi': [str(year)],
	 'q': ['"17 USC"']}
	
	query_str = urllib.urlencode(query_dict, True)
	search_url = host + '/scholar?' + query_str
	print search_url
	# sys.stdout.flush()
		
	while search_url != None:
		print '_new page, year', year
		# sys.stdout.flush()
		time.sleep(0.2 + 0.2*random.random())
		
		response, content = http.request(search_url, 'GET', headers=headers)

		print "Response Status:", resp.status
		# sys.stdout.flush()
		
		if response['status'] in ['302', '503']:
			print "REDIRECT!!"
			search_url = None
			sys.exit(1)
			
		if response['status'] == '200':
			soup = BeautifulSoup(content)
			
			# Just to show where we are
			tt = soup.find('td',{'align':'right'})
			if tt is not None:
				print tt.text, ':: Real count =', count
				# sys.stdout.flush()
	
			# Here taking links with a case href, plus real links (not cited_by) have "onmousedown" field
			# NOTE: Skipping other types of articles with this filter!
			# case_links = soup.findAll(attrs={'href':re.compile("^/scholar_case"), 'onmousedown':True})
			case_links = soup.findAll('a', attrs={'href':re.compile("^/scholar_case"), 'class':re.compile("^yC.+")})
			
			for link in case_links:
	
				# Get rid of the rest of the url query which is about highlighting search terms, etc.
				case_base_url = link['href'].split('&')[0]
				case_num = case_base_url.split('=')[1]
				case_file = case_num + '.html'
				
				# Check if really need to download this file or if it's already in GridFS
				file_list_in_db = list(db.fs.files.find({'filename':case_file},{'_id':True}))
				if len(file_list_in_db) > 0:
					print "already have that one..."
					# sys.stdout.flush()
					continue
				
				# Downloading actual file
				time.sleep(0.2 + 0.2*random.random())
				response, case_html = http.request(host + case_base_url, 'GET', headers=headers)

				if response['status'] in ['302', '503']:
					print "REDIRECT!!"
					search_url = None
					sys.exit(1)
		
				if response['status'] == '200':
					# Write case html to GridFS
					uid = fs.put(case_html, filename=case_file, url=conn.host + case_base_url, media_type='google_scholar_case',year=year)
					# print uid
					# print list(db.fs.files.find())
					count += 1
					print count
					# sys.stdout.flush()
			
			# Getting to following pages
			# Div containing bottom navigation table of links
			nav_div = soup.find('div', {"id" : "gs_n"})
			if nav_div is not None:
				nav_links = nav_div.findAll('a')
				for link in nav_links:
					if link.find('span',{'class':'SPRITE_nav_next'}) != None:
						search_url = host + link['href']
					else:
						search_url = None
			else:
				search_url = None
	
print 'Final count =', count
# sys.stdout.flush()