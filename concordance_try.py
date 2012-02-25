import nltk
import re
import sys
from pymongo import Connection
from pymongo.objectid import ObjectId
from mysolr import Solr

if len(sys.argv) < 2:
	sys.exit("Usage: python concordance_try.py term")
	
# Natural Language Toolkit: code_stemmer_indexing

class IndexedText(object):

    def __init__(self, stemmer, text):
        self._text = text
        self._stemmer = stemmer
        self._index = nltk.Index((self._stem(word), i)
                                 for (i, word) in enumerate(text))

    def concordance(self, word, width=100):
        key = self._stem(word)
        wc = width/4                # words of context
        for i in self._index[key]:
            lcontext = ' '.join(self._text[i-wc:i])
            rcontext = ' '.join(self._text[i:i+wc])
            ldisplay = '%*s'  % (width, lcontext[-width:])
            rdisplay = '%-*s' % (width, rcontext[:width])
            print ldisplay, rdisplay

    def _stem(self, word):
        return self._stemmer.stem(word).lower()


# Make a connection to Mongo.
try:
    # db_conn = Connection("localhost", 27017)
    db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    # sys.stdout.flush()
    sys.exit(1)

db = db_conn['fashion_ip']

# Connection to Solr for faster full text searching
solr = Solr('http://localhost:8080/solr')

qstring = sys.argv[1]

pir_re = re.compile(r'.* ' + qstring + '.*', re.IGNORECASE)
porter = nltk.PorterStemmer()

for year in range(1900,2013):
	print '\nYEAR: ', year
	
	response = solr.search(q=qstring + ' year:' + str(year), fl='_id,score', rows=10000, start=0)
	documents = response.documents
	
	for doc in documents:
		ref = db.docs.find_one({'_id':ObjectId(doc['_id'])},{'content':True,'ref_summary':True})
		s = ref['content']
		
		print
		print ref['ref_summary']
		
		tokens = nltk.word_tokenize(s.lower().encode('utf-8'))
		
		# Stemmed version
		text = IndexedText(porter, tokens)
		text.concordance(qstring)
		
# 		ind = nltk.text.ConcordanceIndex(tokens)		
# 		ind.print_concordance(qstring,width=160,lines=100)
