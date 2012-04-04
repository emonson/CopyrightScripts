#!/usr/bin/env python

"""
Script to move articles (e.g. de, de la, d'...) from before
last name to after first name in Hilary's FileMaker Pro database
through the ODBC connection

Takes in an Excel workbook with three sheets:
	one for the list of articles
	one for the column and table names (Table, ID name, Last name, First name)
	one for name exceptions that should not be changed
	
31 Jan 2012 -- E Monson
"""

from openpyxl import load_workbook
import numpy as N
import os
from pymongo import Connection

# Make a connection to MongoDB
try:
    db_conn = Connection()
    # db_conn = Connection("emo2.trinity.duke.edu", 27017)
except ConnectionFailure:
    print "couldn't connect: be sure that Mongo is running on localhost:27017"
    sys.exit(1)

db = db_conn['fashion_ip']


def n_str(s, a):
	"""Deals with None in first_name"""
	if s is None:
		return unicode(a.strip())
	else:
		return unicode(s.decode('utf8').strip() + ' ' + a.strip())


in_file = '/Users/emonson/Data/ArtMarkets/Katherine/mallet/nonstate_topic_keys_KDD_Edits.xlsx'
doc_topics_file = '/Users/emonson/Data/ArtMarkets/Katherine/mallet/nonstate_copy_200_doc_topics.txt'

# Load in Excel sheet with topic keys
wb = load_workbook(in_file)
sheet = wb.get_sheet_by_name("nonstate_copy_200_topic_keys.tx")

row_tuples = [tuple(xx.value for xx in yy) for yy in sheet.rows]

ntopics = len(sheet.rows)
subject_names = []
subject_vectors = []

for tt in row_tuples:
  subs = tt[0]		# subject string
  top = tt[1]		# topic index
  if subs is not None:
  	# compound subjects separated by commas
  	subs_list = [xx.strip() for xx in subs.split(',')]
  	for sub in subs_list:
			if sub not in subject_names:
				subject_names.append(sub)
				subject_vectors.append(N.zeros(ntopics))
			idx = subject_names.index(sub)
			subject_vectors[idx][top] = 1

# Read in document topics and calculate subject mixtures
file_ids = []
file_subjects = []

for jj, line in enumerate(open(doc_topics_file)):
  # Header line
  if jj == 0:
    continue
    
  ll = line.rstrip().split(' ')
    
  # Get rid of document index
  del ll[0]
  # Grab the file ID
  file_ids.append(os.path.splitext(os.path.basename(ll[0]))[0])
  del ll[0]
  
  # Generate the ordered array of topic weight values
  # (initially ordered by weight rather than by topic)
  weights = N.zeros(ntopics)
  for ii in range(0,len(ll),2):
    weights[int(ll[ii])] = float(ll[ii+1])
  
  # Do a dot product to find the subject overlap
  subject_weights = []
  for ss in subject_vectors:
    subject_weights.append(N.dot(ss,weights))
  
  file_subjects.append(subject_weights)

print "Done computing subject vectors"

# Probably should have output MongoDB docs with _id as name of file
# to make sure it's really unique, but I think the Google Scholar file name
# is also a unique identifier.

# Clear out all subjects first so we don't get leftovers from another analysis
print "Clearing out old subjects"

db.docs.update({},{'$unset':{'subjects':1}})

# Add in new subject weights as name:weight pairs
print "Updating new subjects"

for name, vector in zip(file_ids, file_subjects):
  
  sub_dict = dict(zip(subject_names, vector))
  db.docs.update({'filename':name+'.html'},{'$set':{'subjects':sub_dict}}, upsert=False, multi=False)
    
  