import os
import re
from xml.dom.minidom import parseString
import json
import urllib
import time
import pickle

bib_xml_path = '/Users/emonson/Data/Victoria/CopyrightHistory/BibXML'
file_list = os.listdir(bib_xml_path)

re_nonchar = re.compile(r'[\n\r\t]')	# xml has a lot of extra "formatting" characters
re_parens = re.compile(r' \((.+)\)')
base_req = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&region=%s&sensor=false'
region = 'fr'

places_geocodes = {}
places_docs = {}
doc_places = {}

for doc_num, name in enumerate(file_list):

	print 'Doc', doc_num, '/', len(file_list), '::', name
	# Read bib file
	f = open(os.path.join(bib_xml_path, name), 'r')
	s = f.read()
	f.close()
	
	doc_places[name] = []
	
	# Parse XML
	dom = parseString(s)	# assume have page as string
	
	# Pull out list of "place names referred to" elements
	per_comm_nodes = dom.getElementsByTagName("Place_names_referred_to")[0]
	for node in per_comm_nodes.childNodes:
		if node.nodeType == node.TEXT_NODE:
			tmp_name = re_nonchar.sub(r'',node.data)
			if tmp_name != u'':
				doc_places[name].append(tmp_name)
				# There are sub-information in parentheses in some that we
				# don't want to send to the Google Geocoding API
				# tmp_name2 = re_parens.sub(r'',tmp_name).rstrip()
				tmp_name2 = re_parens.sub(r', \g<1>',tmp_name).rstrip()
				
				if tmp_name not in places_geocodes:
					# Query Google Geocoding API
					time.sleep(0.25)
					url = base_req % (urllib.quote(tmp_name2.encode('utf-8')), region)
					g_reply = urllib.urlopen(url).read()
					g_reply_dict = json.loads(g_reply)
					places_geocodes[tmp_name] = (tmp_name2, g_reply_dict)
					places_docs[tmp_name] = [name]
					
					print '\t'+tmp_name, '"'+tmp_name2+'"', g_reply_dict['status'], len(g_reply_dict['results'])
				else:
					places_docs[tmp_name].append(name)

# Save the {place:(short_name,{'status':XX, 'results':[location results {}s]})} dictionary to disk for later use										
f = open('places_geocodes','w')
pickle.dump(places_geocodes,f)
f.close()

# Save the {place:[docs list]} dictionary to disk for later use										
f = open('places_docs','w')
pickle.dump(places_docs,f)
f.close()

# Save the {doc:[places list]} dictionary to disk for later use										
f = open('docs_places','w')
pickle.dump(doc_places,f)
f.close()

