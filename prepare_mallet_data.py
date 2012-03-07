from pymongo import Connection
import codecs
import re
import os

out_dir = '/Users/emonson/Data/ArtMarkets/Katherine/mallet/Fed_Copyright'

# Make a connection to Mongo.
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']

# Query for subset
fed_re = re.compile(r'^United States Court of', re.IGNORECASE)
query = {'tags':'copyright','$or':[{'court':'Supreme Court of United States.'},{'court':fed_re}]}

# This search chooses which subset
for count,doc in enumerate(db.docs.find(query, {'content':True,'filename':True})):
	if count%100 == 0:
		print count

	out = codecs.open(os.path.join(out_dir, doc['filename'].rstrip('.html')+'.txt'), 'w', 'utf-8')
	out.write(doc['content'])
	out.close()
