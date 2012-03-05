#!/usr/bin/env python

# Write out text (markup) content of all relevant decisions
# to .txt files for processing with Mallet

import os
import couchdb

output_dir = '/Volumes/SciVis_LargeData/ArtMarkets/RelevantContentTxts'
os.makedirs(output_dir)

couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
# couch = couchdb.Server('http://127.0.0.1:5984')
db = couch['copyright_test']

# At this point only decision docs in db, besides design doc
for ii,id in enumerate(db):
	if (ii % 200) == 0:
		print ii
	doc = db[id]
	relevant = False
	if doc.has_key('type') and doc['type'] == 'decision' and doc.has_key('relevant') and doc['relevant'] == True:
		relevant = True
		
	if relevant and doc.has_key('_attachments'):
		atts = doc['_attachments']
		hts = atts.keys()
		# Assuming only one attachment. Grabbing name for name of text file.
		att_name = hts[0]
		base_name = os.path.splitext(att_name)[0]
		output_abs = os.path.join(output_dir, base_name + '.txt')
		
		f = open(output_abs, 'w')
		f.write(doc['content'].encode('utf-8'))
		f.close()

