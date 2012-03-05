# Take in tab-delimited file output by Google Refine, and should
# be able to use the header information to automatically update
# the correct fields. Just set the key_field variable below.

from pymongo import Connection
from pymongo.objectid import ObjectId
import sys
import csv
import re

in_file = sys.argv[1]

database = 'fashion_ip'
collection = 'docs'
key_field = '_id'

oid_re = re.compile('ObjectID\(([a-z0-9]+)\)')

# Make a connection to Mongo.
try:
    db_conn = Connection("localhost")
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn[database]
f = open(in_file, 'r')
csv_reader = csv.reader(f, delimiter='\t')

field_list = csv_reader.next()
key_idx = field_list.index(key_field)
field_id = field_list.pop(key_idx)

# CSV Reader will make each "line" a list
for ii, line in enumerate(csv_reader):
	if ii%100 == 0:
		print ii
	
	id_obj_str = line.pop(key_idx) 	# looks like 'ObjectID(4f406d9e47b230161800017d)'
	id_match = oid_re.match(id_obj_str)
	id = ObjectId(id_match.group(1))
	
	params = {}
	for kk,vv in zip(field_list,line):
		params[kk] = vv
	
	# print {field_id:id}, params
	db.docs.update({field_id:id},{'$set':params}, upsert=False, multi=False)