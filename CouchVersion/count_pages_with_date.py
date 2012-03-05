#!/usr/bin/env python

# Count how many cases are probably copyright related / total number of cases

import os, re
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

data_dir = '/Users/emonson/Data/ArtMarkets/Subset2'

br = re.compile(r'<[bB][rR] *?/>', re.IGNORECASE)
numb_date = re.compile(r'[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
abbr_date = re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
full_date = re.compile(r'(?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4}', re.IGNORECASE)
decid_numb_date = re.compile(r'Decided +[0-9][0-9]?\/[0-9][0-9]?\/[0-9]{2,4}')
decid_abbr_date = re.compile(r'Decided +((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec)\. +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)
decid_full_date = re.compile(r'Decided +((?:January|February|March|April|May|June|July|August|September|October|November|December) +[0-9][0-9]?, +[0-9]{4})', re.IGNORECASE)

def count_files(arg, dirname, files):
		
	for file in files:
		fullpath = os.path.join(dirname, file)
		if os.path.isfile(fullpath) and (file != 'index.html'):
			f = open(fullpath,'r')
			s = f.read()
			f.close()
			soup = BeautifulSoup(s)
			
			# Check for a date field
			# If there is a date field but no date, need to check other places
			# If there are multiple dates, but not a decided date, may need to take non-Denied
			# From multiple date fields need to decide
			# Denied doesn't _always_ come right before the date "Rehearing Denied in No. 23325 April 25, 1955"
			#  (although most often yes)
			date_found = False
			dates_found = soup.findAll("p", "date")
			for bs_piece in dates_found:
				date_field = str(bs_piece)
				date_field = br.sub(' ', date_field)
				print file, date_field
				dates = decid_numb_date.findall(date_field)
				if len(dates) > 0:
					print "\tDecided numb: ", dates
					date_found = True
				dates = decid_abbr_date.findall(date_field)
				if len(dates) > 0:
					print "\tDecided abbr: ", dates
					date_found = True
				dates = decid_full_date.findall(date_field)
				if len(dates) > 0:
					print "\tDecided full: ", dates
					date_found = True
				dates = numb_date.findall(date_field)
				if len(dates) > 0:
					print "\tNumb: ", dates
					date_found = True
				dates = abbr_date.findall(date_field)
				if len(dates) > 0:
					print "\tAbbr: ", dates
					date_found = True
				dates = full_date.findall(date_field)
				if len(dates) > 0:
					print "\tFull: ", dates
					date_found = True
			
			# Should check here first if no date in date field
			if not date_found:
				print file, "PRELIM"
				prelims = soup.find("div", {"class":"prelims"})
				if prelims:
					date_field = str(prelims)
					date_field = br.sub(' ', date_field)
					dates = decid_numb_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided numb: ", dates
						date_found = True
					dates = decid_abbr_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided abbr: ", dates
						date_found = True
					dates = decid_full_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided full: ", dates
						date_found = True
					dates = numb_date.findall(date_field)
					if len(dates) > 0:
						print "\tNumb: ", dates
						date_found = True
					dates = abbr_date.findall(date_field)
					if len(dates) > 0:
						print "\tAbbr: ", dates
						date_found = True
					dates = full_date.findall(date_field)
					if len(dates) > 0:
						print "\tFull: ", dates
						date_found = True
				
			# If haven't found any other dates, then need to check for first date in whole body
			if not date_found:
				print file, "BODY"
				body = soup.body
				if body:
					date_field = str(body)
					date_field = br.sub(' ', date_field)
					dates = decid_numb_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided numb: ", dates
						date_found = True
					dates = decid_abbr_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided abbr: ", dates
						date_found = True
					dates = decid_full_date.findall(date_field)
					if len(dates) > 0:
						print "\tDecided full: ", dates
						date_found = True
					dates = numb_date.findall(date_field)
					if len(dates) > 0:
						print "\tNumb: ", dates
						date_found = True
					dates = abbr_date.findall(date_field)
					if len(dates) > 0:
						print "\tAbbr: ", dates
						date_found = True
					dates = full_date.findall(date_field)
					if len(dates) > 0:
						print "\tFull: ", dates
						date_found = True
				

os.path.walk(data_dir, count_files, None)
