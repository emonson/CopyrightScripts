from pymongo import Connection
import codecs
import re
import os

out_dir = '/Users/emonson/Data/ArtMarkets/Katherine/LDA'

# Regex used later to filter out "bad" words
ncends_re = re.compile(r'^[^a-zA-Z0-9]*([a-zA-Z0-9]+)[^a-zA-Z0-9]*$')
ncall_re = re.compile(r'^[^a-zA-Z]+$')
ncany_re = re.compile(r'[^a-zA-Z]+')

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']

# Stopwords file
f = codecs.open(os.path.join(out_dir,'fashion_stopwords.txt'), 'r', 'utf-8')
# strip off newlines and blank lines
tmp_stopwords = [xx.rstrip('\n') for xx in f.readlines() if xx != '\n']
stopwords = set()
for word in tmp_stopwords:
	if word not in stopwords:
		stopwords.add(word)
f.close()

# Query for subset
fed_re = re.compile(r'^United States Court of', re.IGNORECASE)
query = {'tags':'copyright','$or':[{'court':'Supreme Court of United States.'},{'court':fed_re}]}
# query = {'court':'Supreme Court of United States.','tags':'copyright'}
# Keep an ordered list of terms for readout at end of process
master_terms_list = []
# Keep a dictionary of terms for checking for existence and fast lookup of index in terms list
master_terms_dict = {}
# This is the collection of all document-specific term/count dictionaries
doc_term_tuple_lists = []

total_docs = db.docs.find(query).count()
count = 0
documents = []

# This search chooses which subset
# TODO: Make a version that uses solr for full text search subset
for doc in db.docs.find(query, {'solr_term_list':True,'solr_term_freqs':True}):
	if count%100 == 0:
		print count

	# Filter out stopwords and puctuation
	good_token_counts = [(tt,cc) for (tt,cc) in zip(doc['solr_term_list'],doc['solr_term_freqs']) if ((len(tt) > 2) and (tt not in stopwords) and (not ncall_re.match(tt)))]
	
	# Do this only to keep track of global term list and indices
	# TODO: Need a version that keeps track of total number of docs and total count to filter
	#  out too many and too few...
	for (token,count) in good_token_counts:
		if token not in master_terms_dict:
			master_terms_list.append(token)
			master_terms_dict[token] = len(master_terms_list) - 1
	doc_term_tuple_lists.append(good_token_counts)
	
# Write out data files for Blei LDA

# Terms
out = codecs.open(os.path.join(out_dir,'fashion_terms.txt'), 'w', 'utf-8')
for tt in master_terms_list:
	out.write(tt + u'\n')
out.close()

# Frequencies
out = open(os.path.join(out_dir,'fashion_freq.dat'), 'w')
for term_tuple_list in doc_term_tuple_lists:

	out.write(str(len(term_tuple_list)))
	
	for (term,freq) in term_tuple_list:
		out.write(' ' + str(master_terms_dict[term]) + ':' + str(freq))
	out.write('\n')

		