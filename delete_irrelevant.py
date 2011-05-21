#!/usr/bin/env python

# Update decision relevance based on the presence of "17 U.S.C." 
# copyright code mention

import couchdb

couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
# couch = couchdb.Server('http://127.0.0.1:5984')
db = couch['copyright_test']

kept_count = 0
deleted_count = 0

# At this point only decision docs in db, besides design doc
for ii,id in enumerate(db):
	if (ii % 200) == 0:
		print ii
	if not id.startswith('_'):
		doc = db[id]
		if doc.has_key('relevant') and doc.has_key('type') and doc['type'] == 'decision':
			if doc['relevant'] == False:
				# db.delete(doc)
				deleted_count += 1
			else:
				kept_count += 1

print 'Kept:', kept_count, "Deleted:", deleted_count
