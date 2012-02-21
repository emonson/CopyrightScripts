from pymongo import Connection
import solr

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']

# create a connection to a solr server
s = solr.Solr('http://localhost:8080/solr')

total_docs = db.docs.find().count()
count = 0

for doc in db.docs.find({},{'_id':True,'year':True,'court':True,'url':True,'name':True,'content':True}):
	if count%100 == 0:
		print count
		
	# don't know how else to get solr to take IDs...
	doc['_id'] = str(doc['_id'])
	s.add(doc, commit=False)
	count += 1

s.commit()