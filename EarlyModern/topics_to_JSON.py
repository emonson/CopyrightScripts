# This version produces a list of topics with all data in compact arrays:
# var topics = [
#     { "doc_weights": [ 0.0,  0.0, 0.0,...]
#         "name": 0, 
#         "importance": 0.067320000000000005, 
#         "index": [ 0, 1, 2,...] ... 

import sys
import os
import json
import numpy as N
import re
from operator import itemgetter

analysis_dir = '/Users/emonson/Programming/mallet_hg/mallet'
topic_keys_name = 'cr_topic_keys.txt'
doc_topics_name = 'cr_doc_topics.txt'
out_name = 'cr_data.js'

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


num_docs = len(d_list)
num_topics = len(t_list)

doc_list = []
doc_names_list = []
doc_topic_mtx = N.zeros((num_docs,num_topics))

re_year = re.compile(r'f_([0-9]{4}).*\.txt')

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
	doc_list.append(doc_dict)

topic_list = []
year_list = [doc['year'] for doc in doc_list]
for topic in t_list:
	id = int(topic[0])
	topic_dict = {}
	topic_dict['id'] = id
	topic_dict['importance'] = float(topic[1])
	topic_dict['words'] = topic[2].split(' ')
	topic_dict['doc_weights'] = doc_topic_mtx[:,id].tolist()
	topic_dict['index'] = range(num_docs)
	topic_dict['year'] = year_list
	topic_list.append(topic_dict)

out = open(out_name, 'w')
out.write('var doc_names = ' + json.dumps(doc_names_list, indent=4) + ';\n\n')
out.write('var topics = ' + json.dumps(topic_list, sort_keys=True, indent=4) + ';\n\n')
out.write('var docs = ' + json.dumps(doc_list, sort_keys=True, indent=4) + ';\n\n')
out.close()
