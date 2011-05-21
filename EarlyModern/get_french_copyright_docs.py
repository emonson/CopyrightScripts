# Javascript with data source methods (html links)
# 	http://www.copyrighthistory.org/database/identityhtml/ajax.js

# Main record information page
# Lots of info here, some of which isn't in document identity XML
# 	http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/ausgabe/%22f_1515%22

# Bibliographic record XML  -- similar to main record info page
# Includes info on whether translation/transcriptions exist
# 	http://www.copyrighthistory.org/htdocs/data/bib_record/f_1507.xml

# Document identity XML -- including things like title, full title, date
# 	http://www.copyrighthistory.org/htdocs/data/identity/f_1507.xml

# Document transcription text
# 	http://www.copyrighthistory.org/htdocs/data/transcription/f_1507/f_1507_transc_1_1.txt

# Document translation text
# Not sure what the first number is -- second is a page number
# 	http://www.copyrighthistory.org/htdocs/data/translation/f_1507/f_1507_transl_1_1.txt
# 	http://www.copyrighthistory.org/htdocs/data/translation/f_1763/f_1763_transl_1_45.txt
#
# Can get to first translation page:
# 	http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/showTranslation/%22f_1763%22
# and then search for all in form: %22f_1763_im_001_0045.jpg%22
# and find largest ending number to figure out how many pages exist...

# Commentary -- probably need to gather ending numbers from main info page...
#	-Original html
# 	http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/ausgabeCom/%22f_1761%22
# -Printer-friendly html
# 	http://www.copyrighthistory.org/htdocs/data/commentary/f_1761/f_1761_com_1852008142946.html
# In original commentary page, can search for f_xnum_com_numbers.html...

import re
import os
import time
import urllib
from httplib import HTTP 
from urlparse import urlparse 

# Data directory needs to be specified as an absolute path
data_dir = '/Users/emonson/Data/Victoria/CopyrightHistory'

# Create original data directory tree if doesn't exist
if not os.path.exists(data_dir):
	os.makedirs(data_dir)
	
# Create the directory structure if it doesn't exist
if not os.path.exists(os.path.join(data_dir,'IdentityXML')):
	os.mkdir(os.path.join(data_dir,'IdentityXML'))
if not os.path.exists(os.path.join(data_dir,'BibXML')):
	os.mkdir(os.path.join(data_dir,'BibXML'))
if not os.path.exists(os.path.join(data_dir,'Commentary')):
	os.mkdir(os.path.join(data_dir,'Commentary'))
if not os.path.exists(os.path.join(data_dir,'Transcription')):
	os.mkdir(os.path.join(data_dir,'Transcription'))
if not os.path.exists(os.path.join(data_dir,'Translation')):
	os.mkdir(os.path.join(data_dir,'Translation'))

## From http://code.activestate.com/recipes/101276/
def URL_exists(url): 
	p = urlparse(url) 
	h = HTTP(p[1]) 
	h.putrequest('HEAD', p[2]) 
	h.endheaders() 
	if h.getreply()[0] == 200: 
		return True 
	else:
		return False 


#
# Grab main French language documents page
#
f = urllib.urlopen("http://www.copyrighthistory.org/database/identityhtml/static_link_xml_lang_French.html")
s = f.read()
f.close()

# Pull out all document reference tags (strings) into a list
re_fnum = re.compile(r'%22(f_.+)%22')
tag_list = re_fnum.findall(s)

for doc_id in tag_list:
# for doc_id in ['f_1649']:
	
	print '\n' + doc_id
	
	#
	# Grab, save and parse document bibliographic record XML
	#
	id_xml_name = doc_id + '.xml'
	id_xml_ref = 'http://www.copyrighthistory.org/htdocs/data/bib_record/' + id_xml_name
	time.sleep(0.5)
	f = urllib.urlopen(id_xml_ref)
	s = f.read()
	f.close()
	
	# Save
	os.chdir(os.path.join(data_dir,'BibXML'))
	f = open(id_xml_name,'w')
	print '\tSaving bibliographic record XML: ', id_xml_name
	f.write(s)
	f.close()
	
	# Parse
	from xml.dom.minidom import parseString
	dom = parseString(s)	# assume have page as string
	re_nonchar = re.compile(r'[\n\r\t]')	# xml has a lot of extra "formatting" characters
	
	# Example of pulling out list of elements
	per_comm_nodes = dom.getElementsByTagName("Persons_referred_to_in_commentary")[0]
	per_ref_comm_list = []
	for node in per_comm_nodes.childNodes:
		if node.nodeType == node.TEXT_NODE:
			tmp_name = re_nonchar.sub(r'',node.data)
			if tmp_name != u'':
				per_ref_comm_list.append(tmp_name)
	
	
	# Figure out from here whether translation and transcription exists
	translation_nodes = dom.getElementsByTagName("Show_Translation")[0]
	translation_ON = False
	for node in translation_nodes.childNodes:
		if node.nodeType == node.TEXT_NODE:
			# Should be only one element here
			if re_nonchar.sub(r'',node.data).lower() == 'on':
				translation_ON = True
	print '\tTranslation: ', translation_ON
	
	transcription_nodes = dom.getElementsByTagName("Show_Transcription")[0]
	transcription_ON = False
	for node in transcription_nodes.childNodes:
		if node.nodeType == node.TEXT_NODE:
			# Should be only one element here
			if re_nonchar.sub(r'',node.data).lower() == 'on':
				transcription_ON = True
	print '\tTranscription: ', transcription_ON
	
	#
	# Grab and save identity XML
	#
	id_xml_name = doc_id + '.xml'
	id_xml_ref = 'http://www.copyrighthistory.org/htdocs/data/identity/' + id_xml_name
	s = ''
	time.sleep(0.5)
	f = urllib.urlopen(id_xml_ref)
	s = f.read()
	f.close()
	
	os.chdir(os.path.join(data_dir,'IdentityXML'))
	f = open(id_xml_name,'w')
	print '\tSaving identity XML: ', id_xml_name
	f.write(s)
	f.close()
	
	#
	# Grab html commentary page and figure out commentary text page name from that
	# 
	com_html = 'http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/ausgabeCom/%22' + doc_id + '%22'
	s = ''
	time.sleep(0.5)
	f = urllib.urlopen(com_html)
	s = f.read()
	f.close()
	
	re_com_name = re.compile(doc_id + r'_com_[0-9]+[.]html')
	com_txt_list = re_com_name.findall(s)
	
	# The way their server works, the URL exists for comm page, but returns an error page
	# so have to look for whether there was a match with the file name to know whether commentary
	# really exists
	if len(com_txt_list) > 0:
		s = ''
		# Should only be one, so just using the first in list
		com_txt_name = com_txt_list[0]
		com_txt_ref = 'http://www.copyrighthistory.org/htdocs/data/commentary/' + doc_id + '/' + com_txt_name
		time.sleep(0.5)
		f = urllib.urlopen(com_txt_ref)
		s = f.read()
		f.close()
		
		os.chdir(os.path.join(data_dir, "Commentary"))
		print "\tSaving printer-friendly commentary: ", com_txt_name
		f = open(com_txt_name, 'w')
		f.write(s)
		f.close()
	
	#
	# Grab and concatenate transcription pages if available
	#
	if transcription_ON:
		trans_html_ref = 'http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/showTranscription/%22' + doc_id + '%22'
		s = ''
		time.sleep(0.5)
		print "\tGrabbing main transcription page to find number of pages"
		f = urllib.urlopen(trans_html_ref)
		s = f.read()
		f.close()
		
		# Find all button images
		re_jpg = re.compile(r'%22' + doc_id + r'_im_([0-9]{3})_([0-9]+).jpg%22')
		num_str_list = re_jpg.findall(s)		# [('001', '0001'), ('001', '0045')]
		pre_num = int(num_str_list[0][0])		# assuming all the same numbers...
		num_list = [int(ss[1]) for ss in num_str_list]
		
		trans_txt_name = doc_id + '_transc.txt'
		os.chdir(os.path.join(data_dir, "Transcription"))
		for pg_num in range(1,max(num_list)+1):
			trans_txt_ref = 'http://www.copyrighthistory.org/htdocs/data/transcription/' + doc_id + '/' + doc_id + '_transc_' + str(pre_num) + '_' + str(pg_num) + '.txt'
			s = ''
			time.sleep(0.5)
			f = urllib.urlopen(trans_txt_ref)
			s = f.read()
			f.close()
			
			# some pages in the middle of document don't exist
			re_exists = re.compile(r'not found on this server')
			if not re_exists.search(s):
				print "\t\tSaving text transcription: ", trans_txt_name, ' page ', pg_num
				if pg_num == 1:
					f = open(trans_txt_name, 'w')
				else:
					f = open(trans_txt_name, 'a')
				f.write(s)
				f.close()

	#
	# Grab and concatenate translation pages if available
	#
	if translation_ON:
		trans_html_ref = 'http://www.copyrighthistory.org/cgi-bin/kleioc/0010/exec/showTranslation/%22' + doc_id + '%22'
		s = ''
		time.sleep(0.5)
		print "\tGrabbing main translation page to find number of pages"
		f = urllib.urlopen(trans_html_ref)
		s = f.read()
		f.close()
		
		# Find all button images
		re_jpg = re.compile(r'%22' + doc_id + r'_im_([0-9]{3})_([0-9]+).jpg%22')
		num_str_list = re_jpg.findall(s)		# [('001', '0001'), ('001', '0045')]
		pre_num = int(num_str_list[0][0])		# assuming all the same numbers...
		num_list = [int(ss[1]) for ss in num_str_list]
		
		trans_txt_name = doc_id + '_transl.txt'
		os.chdir(os.path.join(data_dir, "Translation"))
		for pg_num in range(1,max(num_list)+1):
			trans_txt_ref = 'http://www.copyrighthistory.org/htdocs/data/translation/' + doc_id + '/' + doc_id + '_transl_' + str(pre_num) + '_' + str(pg_num) + '.txt'
			s = ''
			time.sleep(0.5)
			f = urllib.urlopen(trans_txt_ref)
			s = f.read()
			f.close()
			
			# some pages in the middle of document don't exist
			re_exists = re.compile(r'not found on this server')
			if not re_exists.search(s):
				print "\t\tSaving text translation: ", trans_txt_name, ' page ', pg_num
				if pg_num == 1:
					f = open(trans_txt_name, 'w')
				else:
					f = open(trans_txt_name, 'a')
				f.write(s)
				f.close()





