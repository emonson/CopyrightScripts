#!/usr/bin/python

import os, stat
import cgi
import cgitb
cgitb.enable()

# Trying to add to PYTHONPATH
import sys
sys.path.insert(0, '/Users/emonson/Programming/VTK_git/VTK/build/bin')
sys.path.insert(0,'/Users/emonson/Programming/VTK_git/VTK/build/Wrapping/Python')

import vtk

form = cgi.FieldStorage()

secret_word = form.getvalue('w','_blank_')
remote_host = os.environ['REMOTE_ADDR']

# Owner ends up being _www and permissions 0644
out_file = '/Users/Shared/junk.txt'
f = open(out_file, 'w')
f.write(secret_word)
f.close()

# File permissions
# st = os.stat('sync_get_NotesJournal.sh')	
# posix.stat_result(st_mode=33188, st_ino=845809, st_dev=234881032L, st_nlink=1, st_uid=501, st_gid=20, st_size=525, st_atime=1281026596, st_mtime=1247759591, st_ctime=1262712197)
# stat.ST_MODE 												# 0
# stat.S_IMODE(st[stat.ST_MODE]) 			# 420
# oct(stat.S_IMODE(st[0])) 	# '0644'
# bin(420)									# '0b110100100'
# os.chmod(out_file, stat.S_IMODE(0b110110110))
os.chmod(out_file, stat.S_IMODE(0o0666))

print "Content-type:text/html\r\n\r\n"
print "<p>Your word is: <b>%s</b> and your IP address is: <b>%s</b></p>" % (secret_word, remote_host)

# print "Content-type:text/html\r\n\r\n"
# print "<html>"
# print "<head>"
# print "<title>Hello - Second CGI Program</title>"
# print "</head>"
# print "<body>"
# print "<h2>Hello %s</h2>" % (secret_word,)
# print "</body>"
# print "</html>"

# $query = new CGI;
# 
# $secretword = $query->param('w');
# $remotehost = $query->remote_host();
# 
# print $query->header;
# print "<p>The secret word is <b>$secretword</b> and your IP is <b>$remotehost</b>.</p>";
# 
