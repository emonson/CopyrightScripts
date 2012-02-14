# Convert grouped by year sums to csv
import json
import csv

f = open('year_sums_17usc.json')
data = json.load(f)
f.close()

f = open('year_sums_17usc.csv','w')
c = csv.writer(f)

c.writerow(["year","total"])

for xx in data:
	c.writerow([xx['year'],xx['Total']])

f.close()