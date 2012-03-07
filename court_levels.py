# Give numeric levels to courts
# 5 = US Supreme Court
# 4 = US Courts of Appeals
# 3 = US District Courts
# 2 = State Courts
# 0 = Unknown or Misc lower

from pymongo import Connection

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']

total_docs = db.docs.find().count()

for count,doc in enumerate(db.docs.find({},{'_id':True,'court':True})):
	if count%100 == 0:
		print count, '/', total_docs
	
	level = 0
	court = doc['court']
	
	# Order is important here...
	if court.startswith('Supreme Court of United States'):
		level = 5
	elif court.startswith('United States Court of Appeals'):
		level = 4
	elif court.startswith('United States District Court'):
		level = 3
	elif court.startswith('United States Court of'):
		level = 3
	elif court.startswith('United States Tax Court'):
		level = 3
	elif court.startswith('United States Bankruptcy Court'):
		level = 3
	elif court.startswith('Temporary Emergency'):
		level = 3
	elif court.startswith('Court of Appeals'):
		level = 2
	elif court.startswith('Supreme Court'):
		level = 2
	elif court.startswith('State Court'):
		level = 2
	elif court.startswith('Tax Court of'):
		level = 2
	elif court.startswith('Superior Court'):
		level = 2
	else:
		level = 0
		
	db.docs.update({'_id':doc['_id']},{'$set':{'court_level':level}}, upsert=False, multi=False)
