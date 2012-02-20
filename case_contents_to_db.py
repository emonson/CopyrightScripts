# from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from pymongo import Connection
from pymongo.dbref import DBRef
import gridfs
import re
from datetime import datetime
import urlparse as UP

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']
fs = gridfs.GridFS(db)

nl_re = re.compile(r'[\r\n]+')
ct_re = re.compile(r'court', re.IGNORECASE)
# NOTE: Right now only checking for full date. Really some abbreviated, and at
# least one like November 1 and 16, 19..
date_re = re.compile(r'([a-zA-Z ]*?):? ?((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})\.?')

total_count = db.fs.files.find({'media_type':'google_scholar_case','processed':False}).count()

# For each original file in 
for ii, case_ref in enumerate(db.fs.files.find({'media_type':'google_scholar_case','processed':False})):
	
	if ii%100 == 0:
		print ii, '/', total_count
		
	uid = case_ref['_id']
	
	# Load in original html using db.fs.get(uid)
	orig_doc = fs.get(uid)
	
	# Create a new dictionary for case object with fields from db.fs.files
	# (filename, media_type, tags, url, year) because don't want to need reference
	# to the GridFS file for this info
	case = {}
	case['filename'] = case_ref['filename']
	case['url'] = case_ref['url']
	case['media_type'] = case_ref['media_type']
	case['tags'] = case_ref['tags']
	case['year'] = case_ref['year']
	
	# Add DBRef to original file for further future processing
	case['file_ref'] = DBRef('fs.files', uid)
	
	# Example of dereferencing that file
	# cr = db.docs.find_one()
	# fs_file_ref = db.dereference(cr['file_ref'])
	# html = fs.get(cr['file_ref'].id).read()
	
	# NOTE: Before try to pull out gsl_opinion, BeautifulSoup has trouble
	# properly closing <center> tags which have child elements...
	# So, replace <center>...</center> with <div class="former_center">...</div>
	# then create soup
	html = orig_doc.read()
	soup = BeautifulSoup(html)
	
	# Pull out "content" from <div id="gsl_opinion" and from that...
	content_div = soup.find('div', {"id" : "gsl_opinion"})
	
	# Strip out all <script> tags so they don't show up in text
	[sc.decompose() for sc in content_div('script')]
	
	# Pull out list of all <center> tags which are direct children of opinion div
	centers = content_div('center')
	
	# Case name from <center><h3 id="gsl_case_name" text and put in case object
	case_name = nl_re.sub(' ', content_div('h3',{'id':'gsl_case_name'})[0].text)
	
	case_nums = []
	collect_nums = True
	docket_num = ''
	docket_url = ''
	court_name = ''
	dates = {}
	for ctr in centers:
		# Stop collecting case numbers if run into h3 indicator of case name
		if ctr.h3 is not None:
			collect_nums = False
			continue
		# Case number(s) are at the beginning
		if collect_nums:
			case_nums.append(ctr.text)
			continue
		# Check for court name, and if so, then grab it and start checking for dates
		court_tmp = ct_re.search(ctr.text)
		if court_tmp is not None:
			court_name = ctr.text
			continue
		# Only collecting docket number if has a link (for now...)
		if (ctr.a is not None) and ('href' in ctr.a) and (ctr.a['href'].startswith('/scholar?scidkt')):
			docket_num = ctr.text
			docket_url = ctr.a['href']
			continue
		# Check for a date and gather what type it is
		date_match = date_re.match(ctr.text)
		if date_match is not None:
			# Change to datetime object (group 0 is whole string)
			proper_date = datetime.strptime(date_match.group(2), "%B %d, %Y")
			if date_match.group(1) == '':
				dates['unlabeled'] = proper_date
			else:
				dates[date_match.group(1).lower()] = proper_date
	
	case['name'] = case_name
	case['numbers'] = case_nums
	case['docket'] = docket_num
	case['docket_url'] = docket_url
	case['court'] = court_name
	case['dates'] = dates
		
	# Remove all page numbers <a class="gsl_pagenum" or "gsl_pagenum2"
	pgs = content_div.findAll(attrs={'class':re.compile(r'^gsl_pagenum')})
	[pp.decompose() for pp in pgs]
	
	# Grab list of all cases referenced
	# Replace all case reference tags with content[0]
	aa = content_div('a')
	ref_case_nums = [UP.parse_qs(UP.urlparse(a['href']).query)['case'][0] for a in aa if (a.has_key('href')) and ('case' in UP.parse_qs(UP.urlparse(a['href']).query))]
	# adding a space before link text to separate footnotes from punctuation
	[a.replace_with(' ' + a.text) for a in aa]
	case['referenced'] = ref_case_nums
	
	# Add content field to case object
	# using content_div.text
	case['content'] = content_div.text
	
	# Grab summary reference text from <div id="gsl_reference" and add to case object
	case['ref_summary'] = soup.find('div',{'id':'gsl_reference'}).text
	
	# Store case object in database
	db.docs.save(case)
	
	# Mark original db.fs.files doc processed = True
	db.fs.files.update({'_id':uid},{'$set':{'processed':True}})