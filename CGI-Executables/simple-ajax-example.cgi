#!/usr/bin/perl -w
use CGI;

$query = new CGI;

$secretword = $query->param('w');
$remotehost = $query->remote_host();
$header = $query->header;

print $query->header;
# print "<p>Header: <b>$header</b></p>"
print "<p>The secret word is <b>$secretword</b> and your IP is <b>$remotehost</b>.</p>";

