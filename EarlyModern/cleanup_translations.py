import re
import os
import glob
import codecs

# NOTE: Manually went through f_1814a_transl.txt 
# and changed one <tab<strong> to <tab><strong>
# and one <stron> to <strong>

data_dir = '/Users/emonson/Data/Victoria/CopyrightHistory/Translation'
clean_dir = os.path.join(data_dir,'Cleaned')

if not os.path.exists(clean_dir):
	os.mkdir(clean_dir)

os.chdir(data_dir)

re_tag = re.compile(r'<.+?>')
re_rn = re.compile(r'\r\n')
re_rr = re.compile(r'\r\r')
re_r = re.compile(r'\r')
re_tabn = re.compile(r'(<tab>)\1*')
re_hyph = re.compile(r'(\w)\r\n[-=](\w)', re.UNICODE)
re_amp = re.compile(r' & ')

# Build up unicode substitution dictionary
u_dict = {}
u_dict[u'\u2026'] = u'...'	# HORIZONTAL ELLIPSIS
u_dict[u'\u0153'] = u'oe'		# LATIN SMALL LIGATURE oe
u_dict[u'\u2013'] = u'--'		# EN DASH
u_dict[u'\u2014'] = u'---'	# EM DASH
u_dict[u'\u2019'] = u"'"		# RIGHT SINGLE QUOTATION MARK
u_dict[u'\u2018'] = u"`"		# LEFT SINGLE QUOTATION MARK
u_dict[u'\u201d'] = u'"'		# RIGHT DOUBLE QUOTATION MARK
u_dict[u'\u201c'] = u'"'		# LEFT DOUBLE QUOTATION MARK
u_dict[u'\ufeff'] = u''			# UTF-8 BYTE OFFSET MARKER (BOM)
u_dict[u'\xa7'] = u'-'			# section sign 
u_dict[u'\xab'] = u'"'			# left-pointing double angle quotation mark
u_dict[u'\xb0'] = u' degree'			# degree sign
u_dict[u'\xba'] = u' rd'			# masculine ordinal indicator
u_dict[u'\xbb'] = u'"'			# right-pointing double angle quotation mark
u_dict[u'\xc2'] = u'A'			# latin capital letter A with circumflex
u_dict[u'\xc9'] = u'E'			# latin capital letter E with acute
u_dict[u'\xdc'] = u'U'			# latin capital letter U with diaeresis
u_dict[u'\xe1'] = u'a'			# latin small letter a with acute
u_dict[u'\xe0'] = u'a'			# latin small letter a with grave
u_dict[u'\xe2'] = u'a'			# latin small letter a with circumflex
u_dict[u'\xe7'] = u'c'			# latin small letter c with cedilla
u_dict[u'\xe9'] = u'e'			# latin small letter e with acute
u_dict[u'\xe8'] = u'e'			# latin small letter e with grave
u_dict[u'\xeb'] = u'e'			# latin small letter e with diaeresis
u_dict[u'\xea'] = u'e'			# latin small letter e with circumflex
u_dict[u'\xed'] = u'i'			# latin small letter i with acute
u_dict[u'\xee'] = u'i'			# latin small letter i with circumflex
u_dict[u'\xef'] = u'i'			# latin small letter i with diaeresis
u_dict[u'\xf4'] = u'o'			# latin small letter o with circumflex
u_dict[u'\xfb'] = u'u'			# latin small letter u with circumflex

for file_name in glob.iglob('f_*_transl.txt'):

	# Read file
	os.chdir(data_dir)
	fu = codecs.open(file_name, 'r', 'utf-8')
	su = fu.read()
	fu.close()
	
	# Remove all hyphenations breaking over lines
	su = re_hyph.sub(r'\g<1>\g<2>', su)
	
	# Remove all \r\n
	su = re_rn.sub(u' ', su)
	
	# All \r\r
	su = re_rr.sub(u' ', su)
	
	# Any extra single \r
	su = re_r.sub(u' ', su)
	
	# Then change all <tab> combinations to \n
	su = re_tabn.sub(u' ', su)
	
	# Then get rid of all other <tags>
	su = re_tag.sub(u' ', su)
	
	# Some documents have ampersands instead of and
	su = re_amp.sub(u' and ', su)
	
	# Then go through dict of all unicodes and replace
	for uc in u_dict:
		r_u = re.compile(uc)
		su = r_u.sub(u_dict[uc], su)
	
	# Write file
	os.chdir(clean_dir)
	out = open(file_name, "w")
	out.write( su.encode("utf-8") )
	out.close()
		
	os.chdir(data_dir)
