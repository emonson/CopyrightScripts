#!/usr/bin/env python

# Update decision relevance based on the presence of "17 U.S.C." 
# copyright code mention

import os, re
import couchdb

# Making this very general just in case...
site = re.compile(r'17 (?:U[. ]?|United )(?:S[. ]?|States )(?:C[. ]?|Code)', re.IGNORECASE)

couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
# couch = couchdb.Server('http://127.0.0.1:5984')
db = couch['copyright_test']

instance_dict = {}

# At this point only decision docs in db, besides design doc
for ii,id in enumerate(db):
	if (ii % 200) == 0:
		print ii
	if not id.startswith('_'):
		doc = db[id]
		if doc.has_key('content') and doc.has_key('date'):
			res = site.findall(doc['content'])
			for ff in res:
				if ff in instance_dict:
					instance_dict[ff] += 1
				else:
					instance_dict[ff] = 1

print instance_dict