# from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from pymongo import Connection
import gridfs
import datetime
# import urlparse as UP

# Make a connection to Mongo.
try:
    db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']
fs = gridfs.GridFS(db)

nl_re = re.compile(r'[\r\n]+')
ct_re = re.compile(r'court', re.IGNORECASE)
date_re = re.compile(r'([a-zA-Z]*?) ?(January|February|March|April|May|June|July|August|September|October|November|December +[0-9][0-9]?, +[0-9]{4})\.')


# For each original file in 
for case_ref in db.fs.files.find({'media_type':'google_scholar_case','processed':False}):
	
	# Load in original html using db.fs.get(uid)
	
	# Create a new dictionary for case object with fields from db.fs.files
	# (filename, media_type, tags, url, year) because don't want to need reference
	# to the GridFS file for this info
	
	# Add DBRef to original file for further future processing
	
	# NOTE: Before try to pull out gsl_opinion, BeautifulSoup has trouble
	# properly closing <center> tags which have child elements...
	# So, replace <center>...</center> with <div class="former_center">...</div>
	# then create soup
	soup = BeautifulSoup(html)
	
	# Pull out "content" from <div id="gsl_opinion" and from that...
	content_div = soup.find('div', {"id" : "gsl_opinion"})
	
	# Strip out all <script> tags so they don't show up in text
	[sc.decompose() for sc in content_div('script')]
	
	# Pull out list of all <center> tags which are direct children of opinion div
	centers = content_div('center')
	
	# Case name from <center><h3 id="gsl_case_name" text and put in case object
	case_name = nl.sub(' ', content_div('h3',{'id':'gsl_case_name'})[0].text)
	
	case_nums = []
	collect_nums = True
	docket_num = ''
	docket_url = ''
	court_name = ''
	start_dates = False
	dates = {}
	for ctr in centers:
		# Case number(s) are at the beginning
		if collect_nums:
			case_nums.append(ctr.text)
			continue
		# Stop collecting case numbers if run into h3 indicator of case name
		if ctr.h3 is not None:
			collect_nums = False
			continue
		# Check for court name, and if so, then grab it and start checking for dates
		court_tmp = ct.search(ctr.text)
		if court_tmp is not None:
			court_name = court_tmp
			start_dates = True
			continue
		# Only collecting docket number if has a link (for now...)
		if (ctr.a is not None) and (ctr.a.href.startswith('/scholar?scidkt')):
			docket_num = ctr.text
			docket_url = ctr.a['href']
			continue
		# Check for a date and gather what type it is
		date_match = date_re.match(ctr.text)
		if date_match is not None:
			# Change to datetime object
			proper_date = datetime.strptime(yy.groups(1), "%B %d, %Y")
			if yy.groups(0) == '':
				dates['Generic'] = proper_date
			else:
				dates[yy.groups(0)] = proper_date
		
	# Remove all page numbers <a class="gsl_pagenum" or "gsl_pagenum2"
	pgs = content_div.findAll(attrs={'class':re.compile(r'^gsl_pagenum')})
	[pp.extract() for pp in pgs]
	
	# Grab list of all cases referenced
	# aa = content_div.findAll('a')
	# [UP.parse_qs(UP.urlparse(a['href']).query)['case'] for a in aa if 'case' in UP.parse_qs(UP.urlparse(a['href']).query)]
	
	# Replace all case reference tags with content[0]
	
	# Run through html2text
	# html2text(unicode(content_div).encode('utf8','ignore'))	
	
	# Remove markup hightlight characters?
	
	# Add content field to case object
	# using content_div.text
	
	# Grab summary reference text from <div id="gsl_reference" and add to case object
	
	# Mark original db.fs.files doc processed = True
