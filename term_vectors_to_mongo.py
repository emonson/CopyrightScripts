# This version taking all term vectors from solr and putting in mongodb
# TODO: Need a version that looks for mongo docs w/o term vector and 
#   only grabs those...

from pymongo import Connection
from pymongo.objectid import ObjectId
from mysolr import Solr
import math
import sys

database = 'fashion_ip'
collection = 'docs'

# Make a connection to Mongo.
try:
    db_conn = Connection("localhost")
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn[database]

solr = Solr('http://emo2.trinity.duke.edu:8080/solr/')

# query = {'q':'*:*','fl':'_id','tv.tf':'true','qt':'tvrh','rows':10,'start':0}
# response = solr.search(**query)
# tv = response.raw_response['termVectors']
# tv[0] == 'warnings'
# tv[1] == [...]

# tv[2] == 'doc-0'
# tv[3] == [...]
# tv[3][0] == 'uniqueKey'
# tv[3][1] == '4f406d8347b2301618000000'
# tv[3][2] == 'content'
# tv[3][3] == ['1', ['tf', 2], '151', ['tf', 1], '157', ['tf', 1], '182', ['tf', 1], '186', ['tf', 2], ...
# tv[4] == 'uniqueKeyFieldName'
# tv[5] == '_id'

# tv[6] == 'doc-1'
# ...
# tv[41] == '_id'

# so, four per doc plus two for warnings...
# seems like can go up to 500 rows without timing out (1000 too many...)
# at about 6 sec/query. Maybe 400 good at about 4 sec...

# Find out how many docs to grab
query = {'q':'*:*','fl':'_id','rows':1,'start':0}
response = solr.search(**query)
inc = 400
print 'Grabbing from', response.total_results, 'solr docs in increments of', inc, 'docs'
pages = int(math.ceil(float(response.total_results)/float(inc)))

for ii in range(pages):
  print ii, '/', pages, '(in groups of', inc, 'docs) starting with', ii*inc
	
  query = {'q':'*:*', 'fl':'_id', 'tv.tf':'true', 'qt':'tvrh', 'rows':inc, 'start':ii*inc}
  response = solr.search(**query)
  tv = response.raw_response['termVectors']
  
  print '\tparsing vectors and updating MongoDB...'
  # Less entries returned on last round
  if len(tv)-2 < 4*inc:
    inc = int((len(tv)-2)/4.0)
  for jj in range(inc):
		idx = jj*4 + 3		# two for warnings and one for doc name
		id = ObjectId(tv[idx][1])
		term_freq_list = tv[idx][3]
		
		term_list = []
		term_freqs = []
		# unpack term frequencies into dictionary
		for tfi in range(0, len(term_freq_list), 2):
		  # TODO: Need to check for '.' in keys -- they are invalid in mongo...
		  #   terms like "u." and "u.s.c." are coming through...
			term_list.append(term_freq_list[tfi])
			term_freqs.append(term_freq_list[tfi+1][1])
			
		db.docs.update({'_id':id},{'$set':{'solr_term_list':term_list,'solr_term_freqs':term_freqs}}, upsert=False, multi=False)
