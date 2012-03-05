#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os, re, shutil
from BeautifulSoup import BeautifulSoup as BS

data_dir = '/Volumes/SciVis_LargeData/ArtMarkets/Original'
sub_dir = 'Subset2'

bad_copyright = re.compile('copyright material omitted|copyrighted material omitted', re.IGNORECASE)
all_copyright = re.compile('copyright', re.IGNORECASE)

num_cases = 0
num_copyright_cases = 0

def count_files(arg, dirname, files):
	global num_cases, num_copyright_cases
	
	print dirname
	dest_dir = dirname.replace('Original', sub_dir)
	os.makedirs(dest_dir)
	
	idx_soup = None
	idx_file = os.path.join(dirname,'index.html')
	if os.path.isfile(idx_file):
		idx_f = open(idx_file, 'r')
		idx_s = idx_f.read()
		idx_f.close()
		idx_soup = BS(idx_s)
		
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			num_cases += 1
			f = open(fullpath,'r')
			s = f.read()
			f.close()
			if len(all_copyright.findall(s)) > len(bad_copyright.findall(s)):
				num_copyright_cases += 1
				dest_path = fullpath.replace('Original', sub_dir)
				shutil.copy(fullpath, dest_path)
			else:
				if idx_soup and idx_soup.find(href=file):
					idx_soup.find(href=file).parent.parent.extract()
	
	if idx_soup:
		idx_file = idx_file.replace('Original', sub_dir)
		idx_f = open(idx_file, 'w')
		idx_f.write(idx_soup.prettify())
		idx_f.close()
	print 'Copyright cases: ', num_copyright_cases, '/', num_cases

os.path.walk(data_dir, count_files, None)
print 'Total Copyright cases: ', num_copyright_cases, '/', num_cases
