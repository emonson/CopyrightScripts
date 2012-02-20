# Convert grouped by year sums to csv
import json
import csv
import os
import sys

if len(sys.argv) < 2:
	sys.exit("Usage: python json2csv.py infile.json")

ap = os.path.abspath(sys.argv[1])

if not os.path.isfile(ap):
	sys.exit("Input file doesn't exist")

file_ext = os.path.splitext(ap)[1]

if file_ext != '.json':
	sys.exit("Input file needs to be .json")

base_dir = os.path.dirname(ap)
base_name = os.path.basename(ap)
csv_name = base_name.rsplit('.',1)[0] + '.csv'

f = open(ap)
data = json.load(f)
f.close()

f = open(os.path.join(base_dir, csv_name) ,'w')
c = csv.writer(f)

c.writerow(["year","total"])

for xx in data:
	c.writerow([xx['year'],xx['Total']])

f.close()