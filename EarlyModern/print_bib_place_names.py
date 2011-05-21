import os
import re
from xml.dom.minidom import parseString

data_path = '/Users/emonson/Data/Victoria/CopyrightHistory/BibXML'
file_list = os.listdir(data_path)

re_nonchar = re.compile(r'[\n\r\t]')	# xml has a lot of extra "formatting" characters
re_parens = re.compile(r'\(.+\)')

for name in file_list:

	# Read
	f = open(os.path.join(data_path,name),'r')
	s = f.read()
	f.close()
	
	# Parse
	dom = parseString(s)	# assume have page as string
	
	# Example of pulling out list of elements
	per_comm_nodes = dom.getElementsByTagName("Place_names_referred_to")[0]
	place_names = []
	for node in per_comm_nodes.childNodes:
		if node.nodeType == node.TEXT_NODE:
			tmp_name = re_nonchar.sub(r'',node.data)
			if tmp_name != u'':
				place_names.append((tmp_name,re_parens.sub(r'',tmp_name).rstrip()))

	print name
	print place_names
	print
