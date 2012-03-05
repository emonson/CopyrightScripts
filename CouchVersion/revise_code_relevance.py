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

num_rel = 0
num_not_rel = 0

# At this point only decision docs in db, besides design doc
for ii,id in enumerate(db):
	if (ii % 200) == 0:
		print ii
	if not id.startswith('_'):
		doc = db[id]
		if doc.has_key('content') and doc.has_key('type') and doc['type'] == 'decision':
			res = site.findall(doc['content'])
			if len(res) > 0:
				doc['relevant'] = True
				db.save(doc)
				num_rel += 1
			else:
				num_not_rel += 1
				doc['relevant'] = False
				db.save(doc)

print 'Relevant:', num_rel, ' Not:', num_not_rel