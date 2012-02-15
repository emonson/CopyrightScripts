#!/usr/bin/env python

# Grab Google Scholar case decisions from search results
# and dump files into GridFS

import httplib
import sys
from BeautifulSoup import BeautifulSoup
import re
import time
from pymongo import Connection
import gridfs
import random
import webbrowser
import urllib
# import urlparse as UP

# If need to update parameters, can do it from here by setting UPDATE_PARAMS=True
UPDATE_PARAMS = True

start_year = 1900
cases_per_page = 100
gs_query_string = '"60 Stat. 427"'
gs_query_tag = 'trademark'

# gs_query_string = '"Trademark Act of 1946"'
# gs_query_tag = 'trademark'
# gs_query_string = '"Trade-Mark Cases, 100 US 82"'
# gs_query_tag = 'trademark'
# gs_query_string = 'trademark OR "trade mark" "15 USC"'
# gs_query_tag = 'trademark'
# gs_query_string = '"17 USC"'
# gs_query_tag = 'copyright'

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

# Grab search year and string from central DB storage
# There should (better) only be one in the DB
if UPDATE_PARAMS:
	# Set params to current year
	db.params.update({'name':'gs_yearbyyear_search'},{'$set':{'start_year':start_year, 'query_string':gs_query_string, 'query_tag':gs_query_tag, 'cases_per_page':cases_per_page}})
else:
	params = db.params.find_one({'name':'gs_yearbyyear_search'})
	start_year = params['start_year']
	cases_per_page = params['cases_per_page']
	gs_query_string = params['query_string']
	gs_query_tag = params['query_tag']

host = 'scholar.google.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0.1) Gecko/20100101 Firefox/8.0.1'}

conn = httplib.HTTPConnection(host)
count = 0

for year in range(start_year,2013):
	
	print "\n** YEAR:", year
	# sys.stdout.flush()
	
	# all courts, one year
	query_dict = {'as_sdt': ['6,34'],
	 'as_vis': ['0'],
	 'btnG': ['Search'],
	 'hl': ['en'],
	 'num': [str(cases_per_page)],
	 'as_ylo': [str(year)],
	 'as_yhi': [str(year)],
	 'q': [gs_query_string]}
	
	query_str = urllib.urlencode(query_dict, True)
	search_url = '/scholar?' + query_str
	print search_url
	# sys.stdout.flush()
		
	while search_url != None:
		print '_new page, year', year
		# sys.stdout.flush()
		time.sleep(0.2 + 0.2*random.random())
		conn.request("GET", search_url, None, headers)
		
		resp = conn.getresponse()
		print "Response Status:", resp.status
		# sys.stdout.flush()
		
		if resp.status == 302:
			# Set params to current year
			db.params.update({'name':'gs_yearbyyear_search'},{'$set':{'start_year':year}})
			
			html = resp.read()
			print "REDIRECT!!"
			soup = BeautifulSoup(html)
			redirect = soup.findAll('a')
			webbrowser.open(redirect[0]['href'])
			search_url = None
			sys.exit(1)
			
		if resp.status == 200:
			html = resp.read()
			soup = BeautifulSoup(html)
			
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
					# Already have it in DB, but might need to update tags list
					# Should only get one return, but doing update on multiple just in case...
					db.fs.files.update({'filename':case_file}, {'$addToSet':{'tags':gs_query_tag}}, multi=True)
					print "already have that one..."
					# sys.stdout.flush()
					continue
				
				# Downloading actual file
				time.sleep(0.2 + 0.2*random.random())
				conn.request("GET", case_base_url, None, headers)
				resp = conn.getresponse()

				if resp.status == 302:
					# Set params to current year
					db.params.update({'name':'gs_yearbyyear_search'},{'$set':{'start_year':year}})
					
					html = resp.read()
					print "REDIRECT!!"
					# sys.stdout.flush()
					soup = BeautifulSoup(html)
					redirect = soup.findAll('a')
					webbrowser.open(redirect[0]['href'])
					search_url = None
					sys.exit(1)
		
				if resp.status == 200:
					case_html = resp.read()
					# print case_html
					# split off case number
					
					# Write case html to GridFS
					uid = fs.put(case_html, filename=case_file, url=conn.host + case_base_url, media_type='google_scholar_case', year=year, tags=[gs_query_tag])
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
						search_url = link['href']
					else:
						search_url = None
			else:
				search_url = None
	
print 'Final count =', count
# sys.stdout.flush()
