#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os
import shutil
# import webbrowser
from BeautifulSoup import BeautifulSoup as BS

data_dir = '/Volumes/SciVis_LargeData/ArtMarkets/Subset2'

num_dups = 0
num_cases = 0
problem_cases = 0

def count_files(arg, dirname, files):
	global num_dups, num_cases
	
	dest_dir = dirname.replace('Subset2', 'Subset2duplicates')
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
		(file_root, file_ext) = os.path.splitext(file)
		dup_name = ''.join([file_root, '_1', file_ext])
		dup_path = os.path.join(dirname, dup_name)
					
		if os.path.isfile(fullpath) and (file != 'index.html'):
			num_cases += 1
		
		if os.path.isfile(fullpath) and os.path.isfile(dup_path):
			num_dups += 1
			# webbrowser.open(fullpath)
			# webbrowser.open(dup_path)
			# choice = raw_input("Hit enter to see the next pair\n>")
			if idx_soup:
				if idx_soup.find(href=file) and not idx_soup.find(href=dup_name):
					# Move _1 file
					dup_dest_path = os.path.join(dest_dir, dup_name)
					shutil.move(dup_path, dup_dest_path)
				elif idx_soup.find(href=dup_name) and not idx_soup.find(href=file):
					# Move std file
					dest_path = os.path.join(dest_dir, file)
					shutil.move(fullpath, dest_path)
				else:
					problem_cases += 1
					print "### Problem: ", file, dup_name


os.path.walk(data_dir, count_files, None)
print 'Number of duplicate files: ', num_dups, '/', num_cases
print 'Number of problems: ', problem_cases