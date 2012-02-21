import nltk
import re
from pymongo import Connection

# Make a connection to Mongo.
try:
    # db_conn = Connection("localhost", 27017)
    db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    # sys.stdout.flush()
    sys.exit(1)

db = db_conn['fashion_ip']

pir_re = re.compile(r'.* piracy.*', re.IGNORECASE)

for year in range(1900,2013):
	print '\nYEAR: ', year
	
	refs = db.docs.find({'year':year, 'content':pir_re})
	
	for ref in refs:
		s = ref['content']
		
		tokens = nltk.word_tokenize(s.lower().encode('utf-8'))
		ind = nltk.text.ConcordanceIndex(tokens)
		
		print
		print ref['ref_summary']
		ind.print_concordance('piracy',width=160,lines=100)
