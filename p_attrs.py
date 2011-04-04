#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os, re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

data_dir = '/Users/emonson/Data/ArtMarkets/Subset2'

attr_dict = {}
attr_dict['blank_attr'] = 0
count = 0

def count_files(arg, dirname, files):
	global attr_dict, count
	
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			
			if (count % 100) == 0:
				print count
				print attr_dict
			count += 1

			f = open(fullpath,'r')
			s = f.read()
			f.close()
			soup = BeautifulSoup(s)
			
			pp = soup.findAll('p')
			
			for p in pp:
				aa = p.attrs
				class_list = [v for k,v in aa if k == 'class']
				if len(class_list) == 0:
					attr_dict['blank_attr'] += 1
				else:
					for val in class_list:
						if attr_dict.has_key(val):
							attr_dict[val] += 1
						else:
							attr_dict[val] = 1
				

os.path.walk(data_dir, count_files, None)
print attr_dict