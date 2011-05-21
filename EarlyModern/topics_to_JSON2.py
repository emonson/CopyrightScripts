# This version produces a list of topics with a separate dict for each data point:
# var topics = [
#     [
#         { "index": 0, "weight": 0.0, "year": 1507 }, 
#         { "index": 1, "weight": 0.0, "year": 1547 }, ...


import sys
import os
import json
import numpy as N
import re
from operator import itemgetter

analysis_dir = '/Users/emonson/Programming/mallet_hg/mallet'
topic_keys_name = 'cr_topic_keys.txt'
doc_topics_name = 'cr_doc_topics.txt'
out_name = 'cr_data2.js'

os.chdir(analysis_dir)

f = open(doc_topics_name, 'r')
sd = f.read().rstrip()
f.close()

f = open(topic_keys_name,'r')
st = f.read().rstrip()
f.close()

tmp_list = sd.split('\n')
# d_list = [ss.rstrip().split(' ') for ss in tmp_list if (len(ss)>0 and ss[0]!='#')]
d_list = [ss.rstrip().split(' ') for ss in tmp_list if ss[0]!='#']

tmp_list = st.split('\n')
t_list = [ss.rstrip().split('\t') for ss in tmp_list]
# Sort by topic "importance"
t_list = sorted(t_list, key=itemgetter(1), reverse=True)
# Get new topic index ordering after sort
topic_idxs = [int(tt[0]) for tt in t_list]

num_docs = len(d_list)
num_topics = len(t_list)

doc_names_list = []
doc_topic_mtx = N.zeros((num_docs,num_topics))

re_year = re.compile(r'f_([0-9]{4}).*\.txt')

# Make a list for all docs, each with a dict containing all topic_weights in a single array
doc_ar_list = []
for doc in d_list:
	id = int(doc[0])
	name = os.path.basename(doc[1])
	doc_dict = {}
	doc_dict['id'] = id
	doc_dict['name'] = name
	doc_dict['year'] = int(re_year.findall(name)[0])
	doc_names_list.append(name)
	for ii in range(2, num_topics+2, 2):
		doc_topic_mtx[id, int(doc[ii])] = float(doc[ii+1])
	doc_dict['topic_weights'] = doc_topic_mtx[id,:].tolist()
	doc_ar_list.append(doc_dict)

# Make a list of docs, where each contains a list of dicts, one for each topic
doc_dict_list = []
for doc in d_list:
	id = int(doc[0])
	weights = doc_topic_mtx[id,:].tolist()	
	this_list = []
	for ii in range(len(weights)):
		doc_dict = {}
		doc_dict['index'] = topic_idxs[ii]
		doc_dict['weight'] = weights[topic_idxs[ii]]	# remap sorted order
		this_list.append(doc_dict)
	doc_dict_list.append(this_list)
	
# Make a list of topics, where each contains a list of dicts, one for each document
topic_list = []
year_list = [doc['year'] for doc in doc_ar_list]
for topic in t_list:
	this_list = []
	id = int(topic[0])
	weights = doc_topic_mtx[:,id].tolist()
	indices = range(num_docs)
	years = year_list
	for ii in range(len(weights)):
		topic_dict = {}
		topic_dict['index'] = indices[ii]
		topic_dict['year'] = years[ii]
		topic_dict['weight'] = weights[ii]
		this_list.append(topic_dict)
	topic_list.append(this_list)

topic_desc_list = []
for topic in t_list:
	this_dict = {}
	this_dict['id'] = int(topic[0])
	this_dict['words'] = topic[2]
	topic_desc_list.append(this_dict)
	
out = open(out_name, 'w')
out.write('var doc_desc = ' + json.dumps(doc_names_list, indent=4) + ';\n\n')
out.write('var docs = ' + json.dumps(doc_dict_list, sort_keys=True, indent=4) + ';\n\n')
out.write('var topic_desc = ' + json.dumps(topic_desc_list, sort_keys=True, indent=4) + ';\n\n')
out.write('var topics = ' + json.dumps(topic_list, sort_keys=True, indent=4) + ';\n\n')
# out.write('var doc_ars = ' + json.dumps(doc_ar_list, sort_keys=True, indent=4) + ';\n\n')
out.close()
