from pymongo import Connection
from datetime import datetime
from elasticsearch import Elasticsearch
import pprint

mongo_db_name = 'fashion_ip'
es_index_name = 'fashion_test'

# Get data directly from MongoDB
# Make a connection to Mongo.
try:
    db_conn = Connection()
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn[mongo_db_name]

# Now also make a connection to Elasticsearch
es = Elasticsearch()

# Create the index
if not es.indices.exists( index = es_index_name ):
    es.indices.create( index = es_index_name )

# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint( es.indices.get_settings( index = es_index_name ) )

# Turn off bulk refresh time for uploads, so can do refresh at the end only
es.indices.put_settings(body={"index": {"refresh_interval": "-1"}}, index = es_index_name)

# Direct from MongoDB method
ii = 0
for doc in db.docs.find({},{'solr_term_list':False, 'solr_term_freqs':False }):
    if ii % 100 == 0:
        print ii
    
    # Replace a couple pieces that ES can't serialize from the mongo object
    id_str = str(doc['_id'])
    doc['_id'] = id_str
    ref_coll = doc['file_ref'].collection
    ref_id_str = str(doc['file_ref'].id)
    doc['file_ref'] = { 'collection':ref_coll, 'id':ref_id_str }

    # Index (or add) the document in Elasticsearch
    res = es.index(index=es_index_name, doc_type='case', id=id_str, body=doc)
    
    ii += 1

# Really update the index
es.indices.refresh(index = es_index_name)

# Turn back on the standard bulk refresh interval
es.indices.put_settings(body={"index": {"refresh_interval": "1s"}}, index = es_index_name)
