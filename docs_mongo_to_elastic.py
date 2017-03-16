import sys
from pymongo import MongoClient
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
import pprint
import time

mongo_db_name = 'fashion_ip'
es_index_name = 'fashion_test'
es_doc_type = 'case'

DRY_RUN = False

# Get data directly from MongoDB
# Make a connection to Mongo.
try:
    client = MongoClient()
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = client[mongo_db_name]

# Now also make a connection to Elasticsearch
host = 'search-dvstest-ssbfvmt2tjfvm7jj6qh2jtmuvi.us-west-2.es.amazonaws.com'
es = Elasticsearch( hosts=[{'host':host, 'port':443}], 
    use_ssl=True, 
    verify_certs=True, 
    connection_class=RequestsHttpConnection
)

# DANGER -- Delete index!!
if not DRY_RUN and es.indices.exists(es_index_name):
    es.indices.delete(es_index_name)

case_mapping = { "properties": {
    "content": { "analyzer": "english", "type": "text" },
    "court": { "type": "keyword" },
    "court_level_name": { "type": "keyword" },
    "court_level": { "type": "integer" },
    "subject_tags": { "type": "keyword" },
    "tags": { "type": "keyword" },
    "year": { "format": "year", "type": "date" }
  }
}

# Create the index
if (not DRY_RUN) and (not es.indices.exists( index = es_index_name )):
    es.indices.create( index = es_index_name, body={ "number_of_shards": 1 } )
    es.indices.put_mapping(index=es_index_name, doc_type=es_doc_type, body=case_mapping)

# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint( es.indices.get_settings( index = es_index_name ) )

# Direct from MongoDB method
ii = 0

start_time = time.time()

for doc in db.docs.find({},{'solr_term_list':False, 'solr_term_freqs':False }):
    if ii % 100 == 0:
        print ii, time.time() - start_time
    
    # Replace a couple pieces that ES can't serialize from the mongo object
    id_str = doc.pop('_id')
    # doc['_id'] = id_str
    ref_coll = doc['file_ref'].collection
    ref_id_str = str(doc['file_ref'].id)
    doc['file_ref'] = { 'collection':ref_coll, 'id':ref_id_str }
    yr = str(doc['year'])
    doc['year'] = yr
    
    # include subject tag in list of strings if weigth greater than 0.01
    if 'subjects' in doc:
        sub_tmp = [k for k,v in doc['subjects'].items() if v >= 0.05]
        if len(sub_tmp) > 0:
            doc['subject_tags'] = sub_tmp
        else:
            doc['subject_tags'] = ['none']
    else:
        doc['subject_tags'] = ['not_analyzed']
    
    # Include human-readable court_level
    if doc['court_level'] == 5:
        doc['court_level_name'] = 'SCOTUS'
    elif doc['court_level'] == 4:
        doc['court_level_name'] = 'US Appeals'
    elif doc['court_level'] == 3:
        doc['court_level_name'] = 'US District'
    elif doc['court_level'] == 2:
        doc['court_level_name'] = 'State'
    else:
        doc['court_level_name'] = 'Unknown'
    
    # Try to put a single real date on each document
    if len(doc['dates']) > 0:
        doc['date_min'] = min(doc['dates'].values())
    else:
        # NOTE: If no date (only 16 of them), use the year, and put it in the middle
        doc['date_min'] = datetime.strptime(str(doc['year'])+'-06-01', '%Y-%m-%d')
    
    # Having trouble with AWS ES limitations of not specifying index and doc type 
    # in bulk call, and python Elasticsearch bulk helper needing it, so trying individual instead
    if not DRY_RUN:
        res = es.index(index=es_index_name, doc_type=es_doc_type, id=id_str, op_type='create', body=doc)
    
    ii += 1

print 'Done:', time.time() - start_time

