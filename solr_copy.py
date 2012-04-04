from pymongo import Connection
from pymongo.errors import ConnectionFailure
# import solr
from mysolr import Solr

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']

# create a connection to a solr server
solr = Solr('http://localhost:8080/solr')

# DELETE ALL DOCS FIRST!!
solr.delete_by_query(query='*:*', commit=True)

total_docs = db.docs.find().count()
count = 0
documents = []

for doc in db.docs.find({},{'_id':True,'year':True,'court':True,'court_level':True,'url':True,'name':True,'content':True,'tags':True,'subjects':True}):
	if count%100 == 0:
		print count
		
	# don't know how else to get solr to take IDs...
	doc['_id'] = str(doc['_id'])
	# include subject tag in list of strings if weigth greater than 0.01
	if 'subjects' in doc:
		sub_tmp = [k for k,v in doc['subjects'].items() if v >= 0.01]
		doc['subjects'] = sub_tmp
	count += 1
	documents.append(doc)

# json indexing supposed to be faster
# at least with mysolr, doing them as a big list is much faster for 18300 docs
# 3 minutes vs 1 min 53 sec
print "updating..."
solr.update(documents,'json',commit=False)
print "committing..."
solr.commit()
print "done..."