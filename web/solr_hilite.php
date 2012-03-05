<?php

// make sure browsers see this page as utf-8 encoded HTML
header('Content-Type: text/html; charset=utf-8');

$limit = 20000;
$query = isset($_REQUEST['q']) ? $_REQUEST['q'] : false;
$additionalParameters = array(
  'fl' => '_id,url,year,name,score',
  'sort' => 'year asc',
  'facet' => 'true',
  'facet.sort' => 'index asc',
  // 'facet.mincount' => '1',
  // notice I use an array for a muti-valued parameter
  'facet.field' => array(
        'year',
    ),
  'hl' => 'on',
  'hl.fl' => 'content',
  'hl.fragsize' => '200',
  'hl.useFastVectorHighlighter' => 'true',
  'hl.boundaryScanner' => 'breakIterator',
  'hl.bs.type' => 'SENTENCE',
  'hl.snippets' => '500'
);

// indent=on
// version=2.2
// q=conceptual+year%3A1970
// fq=
// start=0
// rows=100
// fl=_id%2Cyear%2Cscore
// qt=
// wt=json
// explainOther=
// hl=on
// hl.fl=content
// hl.fragsize=200
// hl.useFastVectorHighlighter=true
// hl.boundaryScanner=breakIterator
// hl.bs.type=CHARACTER
// hl.snippets=100

$results = false;

if ($query)
{
  // The Apache Solr Client library should be on the include path
  // which is usually most easily accomplished by placing in the
  // same directory as this script ( . or current directory is a default
  // php include path entry in the php.ini)
  require_once('Apache/Solr/Service.php');

  // create a new solr service instance - host, port, and webapp
  // path (all defaults in this example)
  $solr = new Apache_Solr_Service('localhost', 8080, '/solr/');

  // if magic quotes is enabled then stripslashes will be needed
  if (get_magic_quotes_gpc() == 1)
  {
    $query = stripslashes($query);
  }

  // in production code you'll always want to use a try /catch for any
  // possible exceptions emitted  by searching (i.e. connection
  // problems or a query parsing error)
  try
  {
    $results = $solr->search($query, 0, $limit, $additionalParameters);
  }
  catch (Exception $e)
  {
    // in production you'd probably log or email this error to an admin
        // and then show a special message to the user but for this example
        // we're going to show the full exception
        die("<html><head><title>SEARCH EXCEPTION</title><body><pre>{$e->__toString()}</pre></body></html>");
  }
  // print_r($results);
  // Can't quite figure out how to dig down to the JSON for docs...?
  // echo json_encode($results->response);
  
  // This gets directly down to the by-year counts from facet
  // JSON dictionary (object) with year as a string key and count as an int value
  // echo json_encode($results->facet_counts->facet_fields->year);
  // This gets an object with _id string keys and value= {'content':['list','of highlight','strings']}
  // echo json_encode($results->highlighting);
}

?>
<html>
  <head>
    <title>PHP Solr Client Example</title>
    <script type="text/javascript" src="d3.v2.min.js"></script>
    <style type="text/css">
    
    body {
    	font-family: sans-serif;
    }
    
    h2 {
    	font-size: 120%;
    	margin: 1.5em 0em 0em 0em;
    	color: DarkGray;
    }
    
    h3 {
    	font-size: 80%;
    	margin: 1em 0em 0em 0em;
    }
    
    a {
    	text-decoration: none;
    }
    
    a:link {
    	color: LightGray;
    }
    
    a:visited {
    	color: #DFD3D3;
    }
    
    a:hover {
    	color: DarkGray;
    }
    
    p.line {
    	margin: 0.5em 0em;
    	font-family: monospace;
    	position: relative;
    	white-space: nowrap;
    }
    
    span.highlight {
    	background: #FFB;
    }
    
    input#q {
    	width: 250px;
    }
    
    </style>
  </head>
  <body>
    <form  accept-charset="utf-8" method="get">
      <label for="q">Search:</label>
      <input id="q" name="q" type="text" value="<?php echo htmlspecialchars($query, ENT_QUOTES, 'utf-8'); ?>"/>
      <input type="submit"/>
    </form>
<?php

// display results
if ($results)
{
  $total = (int) $results->response->numFound;
  $start = min(1, $total);
  $end = min($limit, $total);
  $current_year = 0;
?>
    <div>Results <?php echo $start; ?> - <?php echo $end;?> of <?php echo $total; ?>:</div>
<?php
  // iterate result documents
  foreach ($results->response->docs as $doc)
  {
		$doc_id = $doc->_id;
		if ($doc->year !== $current_year)
		{
			$current_year = $doc->year;
?>

<h2><?php echo $doc->year; ?></h2>

<?php
		}
?>
<h3>
<a href="http://<?php echo $doc->url; ?>"><?php echo htmlspecialchars(substr($doc->name,0,80), ENT_NOQUOTES, 'utf-8'); ?></a>
</h3>
<?php
    foreach ($results->highlighting->$doc_id->content as $snippet)
    {
    	$new_snip = stripslashes(trim($snippet));
    	$new_snip = str_replace("\n", " ", $new_snip);
    	// $new_spl = explode("<span", $new_snip);
    	// $hi_offset = strlen($new_spl[0]);
    	$hi_offset = stripos($new_snip, "<span");
    	$left_pos = 40.7853 - 0.615635*$hi_offset
    	
?>
<p class="line" style="left: <?php echo "$left_pos"; ?>em" ><?php echo $new_snip; ?></p>
<?php
    }
  }
}
?>
  </body>
</html>