from BeautifulSoup import BeautifulSoup
from pymongo import Connection
import gridfs
# import urlparse as UP

# Make a connection to Mongo.
try:
    db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']
fs = gridfs.GridFS(db)

# For each original file in 
# db.fs.files.find({'media_type':'google_scholar_case','processed':False})

# Load in original html using db.fs.get(uid)

# Create a new dictionary for case object with fields from db.fs.files
# (filename, media_type, tags, url, year) because don't want to need reference
# to the GridFS file for this info

# Add DBRef to original file for further future processing

# NOTE: Before try to pull out gsl_opinion, BeautifulSoup has trouble
# properly closing <center> tags which have child elements...
# So, replace <center>...</center> with <div class="former_center">...</div>

# Pull out "content" from <div id="gsl_opinion" and from that...
# content_div = soup.find('div', {"id" : "gsl_opinion"})

	# Pull out list of all <center> tags which are direct children of opinion div

		# Case number from first(and more) <center><b> in div
		
		# Case name from <center><h3 id="gsl_case_name" text and put in case object
		
		# Docket number from third <center>(sometimes)<a href="/scholar?scidkt=...">
		
		# Court from fourth <center>
		
	# Remove all page numbers <a class="gsl_pagenum" or "gsl_pagenum2"
	# pgs = content_div.findAll(attrs={'class':re.compile(r'^gsl_pagenum')})
	# [pp.extract() for pp in pgs]
	
	# Grab list of all cases referenced
	# aa = content_div.findAll('a')
	# [UP.parse_qs(UP.urlparse(a['href']).query)['case'] for a in aa if 'case' in UP.parse_qs(UP.urlparse(a['href']).query)]
	
	# Replace all case reference tags with content[0]
	
	# Run through html2text
	# html2text(unicode(content_div).encode('utf8','ignore'))	

	# Remove markup hightlight characters?
	
# Add content field to case object

# Grab summary reference text from <div id="gsl_reference" and add to case object