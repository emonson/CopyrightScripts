import sys
from pymongo import Connection
from datetime import datetime
from elasticsearch import Elasticsearch
import pprint

mongo_db_name = 'fashion_ip'
es_index_name = 'fashion_test'
es_doc_type = 'case'

DRY_RUN = False

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

# DANGER -- Delete index!!
if not DRY_RUN:
    es.indices.delete(es_index_name)

case_mapping = { "properties": {
    "content": { "analyzer": "english", "type": "string" },
    "court": { "index": "not_analyzed", "type": "string" },
    "court_level_name": { "index": "not_analyzed", "type": "string" },
    "court_level": { "type": "integer" },
    "subject_tags": { "index": "not_analyzed", "type": "string" },
    "tags": { "index": "not_analyzed", "type": "string" },
    "year": { "format": "year", "type": "date" }
  }
}

# Create the index
if not es.indices.exists( index = es_index_name ):
    es.indices.create( index = es_index_name )
    es.indices.put_mapping(index=es_index_name, doc_type=es_doc_type, body=case_mapping)


# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint( es.indices.get_settings( index = es_index_name ) )

# Turn off bulk refresh time for uploads, so can do refresh at the end only
if not DRY_RUN:
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
    
    # Index (or add) the document in Elasticsearch
    if not DRY_RUN:
        res = es.index(index=es_index_name, doc_type=es_doc_type, id=id_str, body=doc)
    
    ii += 1

# Really update the index
if not DRY_RUN:
    es.indices.refresh(index = es_index_name)

# Turn back on the standard bulk refresh interval
if not DRY_RUN:
    es.indices.put_settings(body={"index": {"refresh_interval": "1s"}}, index = es_index_name)
