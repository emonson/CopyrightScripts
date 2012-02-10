from BeautifulSoup import BeautifulSoup
import os
from html2text import html2text

os.chdir('/Users/emonson/Data/ArtMarkets/Katherine/FashionCases')

ls = os.listdir('.')
s = ''
for f in ls:
	if f.endswith('.html'):
		orig_html = open(f,'r').read()
		soup = BeautifulSoup(orig_html)
		content_div = soup.find('div', {"id" : "gsl_content"})

		s += html2text(unicode(content_div).encode('utf8','ignore'))
	
f = open('CaseTexts.txt','w')
f.write(s)
f.close()

