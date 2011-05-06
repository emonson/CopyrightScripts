#!/usr/bin/env python

# Update decision relevance based on the presence of "17 U.S.C." 
# copyright code mention

import couchdb

couch = couchdb.Server('http://emonson:couchlog@127.0.0.1:5984')
# couch = couchdb.Server('http://127.0.0.1:5984')
db = couch['copyright_test']

res = db.view('copyright_test/years_courts', group_level=2)

data = {}

for row in res.rows:
	year = row.key[0]
	court = row.key[1]
	count = row.value
	
	if year not in data:
		data[year] = [0]*15;
	else:
		data[year][court] = count

f = open('years_courts.csv', 'w')
yrs = data.keys()
yrs.sort()

for yr in yrs:
	d = [yr]
	d.extend(data[yr])
	ds = str(d)
	f.write(ds[1:-1] + "\n")

f.close()

# Years only

res = db.view('copyright_test/years_courts', group_level=1)

f = open('years.csv', 'w')

for row in res.rows:
	f.write(str(row.key[0]) + "," + str(row.value) + "\n")

f.close()
