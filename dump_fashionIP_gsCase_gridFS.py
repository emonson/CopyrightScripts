#!/usr/bin/env python

# Grab Google Scholar case decisions from search results
# and dump files into GridFS

import httplib
from BeautifulSoup import BeautifulSoup
import re
import time
from pymongo import Connection
import gridfs
import random
import webbrowser


# DEBUG: Change to .fashion_ip for real cases!
db = Connection().test
fs = gridfs.GridFS(db)

host = 'scholar.google.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:8.0.1) Gecko/20100101 Firefox/8.0.1'}

# "conceptual separability" design, all courts
search_url = ''

conn = httplib.HTTPConnection(host)
count = 0

while search_url != None:
	print '\nNew Page\n'
	time.sleep(1.0*(random.random() + 1))
	conn.request("GET", search_url, None, headers)
	
	resp = conn.getresponse()
	print "Response Status:", resp.status
	
	if resp.status == 302:
		html = resp.read()
		print "REDIRECT!!"
		soup = BeautifulSoup(html)
		redirect = soup.findAll('a')
		webbrowser.open(redirect[0]['href'])
		search_url = None
		
	if resp.status == 200:
		html = resp.read()
		print html
		soup = BeautifulSoup(html)
		
		# Just to show where we are
		tt = soup.find('td',{'align':'right'})
		print tt.text, ':: Real count =', count

		# Here taking links with a case href, plus real links (not cited_by) have "onmousedown" field
		# NOTE: Skipping other types of articles with this filter!
		case_links = soup.findAll(attrs={'href':re.compile("^/scholar_case"), 'onmousedown':True})
		
		for link in case_links:

			# Get rid of the rest of the url query which is about highlighting search terms, etc.
			case_base_url = link['href'].split('&')[0]
			
			# Downloading actual file
			time.sleep(1.0*(random.random() + 1))
			conn.request("GET", case_base_url, None, headers)
			resp = conn.getresponse()
			if resp.status == 200:
				case_html = resp.read()
				# print case_html
				# split off case number
				case_num = case_base_url.split('=')[1]
				
				# Write case html to GridFS
				uid = fs.put(case_html, filename=case_num + '.html', url=conn.host + case_base_url, media_type='google_scholar_case')
				# print uid
				# print list(db.fs.files.find())
				count += 1
				print count,
				if count%10 == 0:
					print
		
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
