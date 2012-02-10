import urllib
import urlparse as UP
import httplib
from BeautifulSoup import BeautifulSoup
import re
import time
from pymongo import Connection
import gridfs

db = Connection().fashion_ip
fs = gridfs.GridFS(db)

host = 'scholar.google.com'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'}

# "conceptual separability", all courts
url = 'http://scholar.google.com/scholar?as_q=&num=10&as_epq=conceptual%20separability&as_oq=&as_eq=&as_occt=any&as_sauthors=&as_publication=&as_ylo=&as_yhi=&btnG=Search%20Scholar&hl=en&allcts=&as_sdt=6'

conn = httplib.HTTPConnection(host)

while url != None:
	print 'delaying query'
	time.sleep(0.2)
	conn.request("GET", url, None, headers)
	
	resp = conn.getresponse()
	
	if resp.status == 200:
		html = resp.read()
		
		soup = BeautifulSoup(html)

		# Here taking links with a case href, plus real links (not cited_by) have "onmousedown" field
		# NOTE: Skipping other types of articles with this filter!
		case_links = soup.findAll(attrs={'href':re.compile("^/scholar_case"), 'onmousedown':True})
		
		for link in case_links:

			# Get rid of the rest of the url query which is about highlighting search terms, etc.
			case_base_url = link['href'].split('&')[0]
			
			time.sleep(0.2)
			conn.request("GET", case_base_url, None, headers)
			resp = conn.getresponse()
			if resp.status == 200:
				case_html = resp.read()
				# print case_html
				# split off case number
				case_num = case_base_url.split('=')[1]
				f = open(case_num + '.html', 'w')
				f.write(case_html)
				f.close()
		
		# Getting to following pages
		# Div containing bottom navigation table of links
		nav_div = soup.find('div', {"id" : "gs_n"})
		nav_links = nav_div.findAll('a')
		for link in nav_links:
			if link.find('span',{'class':'SPRITE_nav_next'}) != None:
				url = link['href']
			else:
				url = None


