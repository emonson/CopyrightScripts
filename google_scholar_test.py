import urllib
import httplib
from BeautifulSoup import BeautifulSoup
import re

case_addr = re.compile('(/scholar_case\?case=[0-9]+)&')

# http://scholar.google.com/scholar?as_q=&num=100&btnG=Search+Scholar&as_epq=17+USC&as_oq=&as_eq=&as_occt=any&as_sauthors=&as_publication=&as_ylo=2004&as_yhi=2004&as_sdt=3&as_sdtf=56%2C57&as_sdts=34&hl=en

host = 'scholar.google.com'
# base_url = '/scholar'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'}

# p = {}
# p['as_q'] = ''
# p['num'] = 100
# p['btnG'] = 'Search+Scholar'
# p['as_epq'] = '17+USC'
# p['as_oq'] = ''
# p['as_eq'] = ''
# p['as_occt'] = 'any'
# p['as_sauthors'] = ''
# p['as_publication'] = ''
# p['as_ylo'] = 2004
# p['as_yhi'] = 2004
# p['as_sdt'] = 3
# p['as_sdtf'] = '56+C57'
# p['as_sdts'] = 34
# p['hl'] = 'en'
# 
# params = urllib.urlencode(p)

# as_q=&num=100&as_epq=17+USC&as_oq=&as_eq=&as_occt=any&as_sauthors=&as_publication=&as_ylo=2004&as_yhi=2004&as_sdt=3&as_sdtf=56%2C57&as_sdts=34&btnG=Search+Scholar&hl=en&num=100
# 
# p = []
# p.append('as_eq=')
# p.append('as_occt=any')
# p.append('as_sauthors=')
# p.append('as_publication=')
# p.append('as_ylo=2004')
# p.append('as_yhi=2004')
# p.append('as_sdt=3')
# p.append('as_sdtf=56%2C57')
# p.append('as_sdts=34')
# p.append('btnG=Search+Scholar')
# p.append('hl=en')
# p.append('num=100')
# 
# params = "&".join(p)
# 
# url = base_url + "?" + params
# 
# print url

url = '/scholar?hl=en&num=100&q=%2B%2217+USC%22&btnG=Search&as_sdt=4%2C56%2C57&as_ylo=1994&as_yhi=1994&as_vis=0'
# url = '/scholar?hl=en&num=100&q=%2217+USC%22&btnG=Search&as_sdt=4%2C56%2C57&as_ylo=2006&as_yhi=2006&as_vis=0'

conn = httplib.HTTPConnection(host)
conn.request("GET", url, {}, headers)

resp = conn.getresponse()

if resp.status == 200:
	html = resp.read()
	
	f = open('g1994.html', 'w')
	f.write(html)
	f.close()
	
	soup = BeautifulSoup(html)
	# Looks like <div class=gs_r> </div> encloses each full result record
	# and <div class=gs_rt> </div> encloses each result title & link
	
	# Here taking links with a case href, plus real links (not cited_by) have "onmousedown" field
	cases_list = soup.findAll(attrs={'href':re.compile("^/scholar_case"), 'onmousedown':True})
	
	# TODO: Should really also search within returned summary for 17 USC string...
	
	
	for ii, case in enumerate(cases_list):
		addr = case_addr.findall(case['href'])
		print ii, addr[0]
		

