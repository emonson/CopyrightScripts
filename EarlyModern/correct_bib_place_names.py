import os, sys
import re
import json
import urllib
import time
import pickle
import webbrowser
import nltk

places_page_dir = '/Users/emonson/Programming/Python/DocAnalysis/Victoria/Protovis'
places_page = 'place_label.html'
places_data = 'places.js'
doc_transl_dir = '/Users/emonson/Data/Victoria/CopyrightHistory/Translation/Cleaned'

# UTILITY FUNCTIONS

def display_place_info(p_dict, key):
	print '- - - - - - - - - - -\nCurrent location information:\n'
	print key, ': "'+p_dict[key][0]+'"'
	for ii, entry in enumerate(p_dict[key][1]['results']):
		print str(ii+1)+'.', entry['formatted_address'], 
		print '(', 
		for pl_detail in entry['types']:
			print pl_detail,
		print ')'
	print

def simple_place_info(p_dict, key, idx=None):
	print key, ': "'+p_dict[key][0]+'"'
	for ii, entry in enumerate(p_dict[key][1]['results']):
		if idx is None:
			print entry['formatted_address'], 
		else:
			print str(idx+1)+'.', entry['formatted_address'], 
		print '(', 
		for pl_detail in entry['types']:
			print pl_detail,
		print ')'
	print

def display_place_concordances(places_docs, place, con_dict):
	print '\n===================\nPlace mentions in document contexts for', place.split()[0] + ':\n'
	docs_list = places_docs[place]
	for doc in docs_list:
		print "Document:", doc.rstrip('.xml')
		if doc in con_dict:
			ind = con_dict[doc]
			ind.print_concordance(place.split()[0])
		else:
			print 'No translation...'
		print

def generate_place_data_file(p_dict, key):
	p_list = []
	lat_list = []
	lng_list = []
	for ii, entry in enumerate(p_dict[key][1]['results']):
		location = entry['geometry']['location']
		j_dict = {}
		j_dict['label'] = str(ii+1)
		j_dict['lat'] = location['lat']
		j_dict['lon'] = location['lng']
		p_list.append(j_dict)
		lat_list.append(location['lat'])
		lng_list.append(location['lng'])
	j_str = json.dumps(p_list,indent=4)
	lat_str = json.dumps({'min':min(lat_list), 'max':max(lat_list)})
	lng_str = json.dumps({'min':min(lng_list), 'max':max(lng_list)})
	ctr_str = json.dumps({'lat':float(sum(lat_list))/float(len(lat_list)), 'lng':float(sum(lng_list))/float(len(lng_list))})
	f = open(os.path.join(places_page_dir,places_data),'w')
	f.write('var mentioned_locations = '+j_str+';\n\n')
	f.write('var lat_range = ' + lat_str + ';\n\n')
	f.write('var lng_range = ' + lng_str + ';\n\n')
	f.write('var mean_pos = ' + ctr_str + ';\n\n')
	f.close()

def generate_single_places_data_file(p_dict, key_list):
	p_list = []
	lat_list = []
	lng_list = []
	for ii, p_key in enumerate(key_list):
		if len(p_dict[p_key][1]['results']) > 0:
			# NOTE: Only taking first entry for now...
			entry = p_dict[p_key][1]['results'][0]
			location = entry['geometry']['location']
			j_dict = {}
			j_dict['label'] = str(ii+1)
			j_dict['lat'] = location['lat']
			j_dict['lon'] = location['lng']
			p_list.append(j_dict)
			lat_list.append(location['lat'])
			lng_list.append(location['lng'])
	j_str = json.dumps(p_list,indent=4)
	lat_str = json.dumps({'min':min(lat_list), 'max':max(lat_list)})
	lng_str = json.dumps({'min':min(lng_list), 'max':max(lng_list)})
	ctr_str = json.dumps({'lat':float(sum(lat_list))/float(len(lat_list)), 'lng':float(sum(lng_list))/float(len(lng_list))})
	f = open(os.path.join(places_page_dir,places_data),'w')
	f.write('var mentioned_locations = '+j_str+';\n\n')
	f.write('var lat_range = ' + lat_str + ';\n\n')
	f.write('var lng_range = ' + lng_str + ';\n\n')
	f.write('var mean_pos = ' + ctr_str + ';\n\n')
	f.close()

def google_query(query):
		url = base_req % (urllib.quote(query.encode('utf-8')), region)
		g_reply = urllib.urlopen(url).read()
		g_reply_dict = json.loads(g_reply)
		return g_reply_dict

def resolve_entry(places_geocodes, place):
	# Print concordance info only the first time around
	display_place_concordances(places_docs, place, con_dict)
	done = False
	
	while not done:
		results = places_geocodes[place][1]['results']
		num_results = len(results)
		old_str = places_geocodes[place][0]
		
		display_place_info(places_geocodes, place)
		if num_results != 0:
			generate_place_data_file(places_geocodes, place)
			webbrowser.open(os.path.join(places_page_dir,places_page))
		
		if num_results == 0:
			choice = raw_input("Enter a new Google geocoding search string\n>")
		else:
			choice = raw_input("""Enter the location number to verify that choice
or just hit <return> to keep the current results and move on
or type "exit" (without the quotes) to stop and save the current state
or enter a new Google geocoding search string to try again
>""")
		
		if len(choice) == 0:
			done = True
			return 'continue'
		
		try:
				number = int(choice.strip().split()[0])
		except (ValueError, IndexError):
				number = None
		
		if number is not None:
			if number <= num_results and number > 0:
				places_geocodes[place][1]['results'] = [results[number-1]]
				done = True
			else:
				print "Invalid choice, try again..."
		elif choice == 'exit':
			done = True
			return 'exit'
		else:
			g_reply_dict = google_query(choice.decode('utf-8'))
			places_geocodes[place] = (choice, g_reply_dict)
			print "\nResults of new search:"
			
			# NOTE: Some sort of problem caching old page on 1st re-search...
	
	return 'continue'

# MAIN ROUTINE

# Load the {place:(short_name,{'status':XX, 'results':[location results {}s]})} dictionary to disk for later use										
f = open('places_geocodes','r')
places_geocodes = pickle.load(f)
f.close()

# Save a backup of the dictionary to disk for later use										
f = open('places_geocodes_backup_'+str(int(time.time())),'w')
pickle.dump(places_geocodes,f)
f.close()

# Load the {place:[docs list]} dictionary to disk for later use										
f = open('places_docs','r')
places_docs = pickle.load(f)
f.close()

# Load the {doc:[places list]} dictionary to disk for later use										
f = open('docs_places','r')
doc_places = pickle.load(f)
f.close()

base_req = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&region=%s&sensor=false'
region = 'fr'

# Build concordance index for each document
# Note that not all documents have a translation for now...
# Also, if the corpus is bigger, it'd be better to pre-calculate these
#  when doing the initial data gathering instead of here...
doc_transl_list = os.listdir(doc_transl_dir)
con_dict = {}

print 'Building concordance indices...'
for name in doc_transl_list:
	f = open(os.path.join(doc_transl_dir,name), 'r')
	s = f.read()
	f.close()
	tokens = nltk.word_tokenize(s)
	ind = nltk.text.ConcordanceIndex(tokens)
	# Keying off xml name instead of original translation file name
	xml_name = name.rstrip('_transl.txt') + '.xml'
	con_dict[xml_name] = ind
print 'Done\n'

# Calculate summaries of results
num_zeros = len([k for k,v in places_geocodes.items() if len(v[1]['results']) == 0])
num_multiples = len([k for k,v in places_geocodes.items() if len(v[1]['results']) > 1])
num_singles = len([k for k,v in places_geocodes.items() if len(v[1]['results']) == 1])

print "Summary of Current Results:"
print '\t', num_zeros, 'places with Zero results'
print '\t', num_multiples, 'places with Multiple results'
print '\t', num_singles, 'places with a Single result'
print '\t', len(places_geocodes), 'total'

mode = raw_input("""Select mode number
or enter a full place name to check only that item:
1. Check zeros
2. Check multiples
3. Check singles
4. Map all singles
5. Check all
> """)

# Test if an integer was entered
try:
		number = int(mode.strip().split()[0])
except (ValueError, IndexError):
		number = None
		
# Check zeros
if number == 1:
	place_keys = [k for k,v in places_geocodes.items() if len(v[1]['results']) == 0]

# Check multiples
elif number == 2:
	place_keys = [k for k,v in places_geocodes.items() if len(v[1]['results']) > 1]

# Check singles
elif number == 3:
	place_keys = [k for k,v in places_geocodes.items() if len(v[1]['results']) == 1]

# Map all singles
elif number == 4:
	single_places = [k for k,v in places_geocodes.items() if len(v[1]['results']) == 1]
	# Map
	if len(single_places) > 0:
		generate_single_places_data_file(places_geocodes, sorted(single_places))
		webbrowser.open(os.path.join(places_page_dir,places_page))
	# List
	for ii, place in enumerate(sorted(single_places)):
		simple_place_info(places_geocodes, place, ii)
	place_keys = []

# Check all
elif number == 5:
	place_keys = places_geocodes.keys()

# Investigate a single entry
elif (number is None):
	# Try to use the string to match a place in the data
	if mode in places_geocodes:
		place_keys = [mode]
	else:
		place_keys = [k for k,v in places_geocodes.items() \
		      if (mode.lower() in k.lower()) or (mode.lower() in v[0].lower())]
		if len(place_keys) == 0:
			print "Unknown mode or place name"
			sys.exit(1)

# Loop through resulting place_keys and give a chance to fix each
for place in sorted(place_keys):
	keep_going = resolve_entry(places_geocodes, place)
	if keep_going == 'exit':
		break

# TODO: For now always doing this unless sys.exit(), but probably should have a flag...
# Save the {place:(short_name,{'status':XX, 'results':[location results {}s]})} dictionary to disk for later use										
f = open('places_geocodes','w')
pickle.dump(places_geocodes,f)
f.close()
