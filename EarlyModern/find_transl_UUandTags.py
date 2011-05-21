import re
import os
import glob
import codecs

data_dir = '/Users/emonson/Data/Victoria/CopyrightHistory/Translation'

os.chdir(data_dir)

re_u = re.compile(u'[\u0080-\uffff]')
re_tag = re.compile(r'<.+?>')

all_u = set()
all_tag = set()

for file in glob.iglob('f_*_transl.txt'):
	fu = codecs.open(file,'r','utf-8')
	su = fu.read()
	fu.close()
	
	this_u_list = re_u.findall(su)
	this_tag_list = re_tag.findall(su)
	
	for uchar in this_u_list:
		all_u.add(uchar)
	
	for tag in this_tag_list:
		all_tag.add(tag)
		
print all_u
print all_tag

