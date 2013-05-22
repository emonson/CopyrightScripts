<?php

// make sure browsers see this page as utf-8 encoded HTML
header('Content-Type: text/html; charset=utf-8');

$casesperpage = 200;
$query = isset($_REQUEST['q']) ? $_REQUEST['q'] : false;
$filter = isset($_REQUEST['fq']) ? $_REQUEST['fq'] : "";
$start = isset($_REQUEST['start']) ? $_REQUEST['start'] : 0;
$min_ct = isset($_REQUEST['min_ct']) ? $_REQUEST['min_ct'] : 2;
if ($min_ct > 5) { $min_ct = 5; }
if ($min_ct < 0) { $min_ct = 0; }

$additionalParameters = array(
  'fl' => '_id,url,year,name,score,court_level,tags,subjects',
  'fq' => array("{!tag=dt}court_level:[$min_ct TO 5]",
                $filter ),
  // court_level: 5 = US Supreme, 4 = US Courts of Appeals, 3 = US District, 2 = State, 0 = Misc
  'sort' => 'year asc',
  'facet' => 'true',
  'facet.sort' => 'index asc',
  'facet.limit' => '1000',
  // 'facet.mincount' => '1',
  // notice I use an array for a muti-valued parameter
  'facet.field' => array(
        '{!ex=dt}court_level',
        'year',
        'tags',
        'subjects'
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
    $results = $solr->search($query, $start, $casesperpage, $additionalParameters);
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
    <script type="text/javascript" src="d3_2.8.1/d3.v2.min.js"></script>
    <style type="text/css">
    
    body {
    	font-family: sans-serif;
    }
    
    label {
    	font-size: 80%;
    }
    
    ul {
    	font-size: 70%;
    	padding: 0px;
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
    
    a.pagenav {
    	font-size: 60%;
    }
    
    a.pagenav:link {
    	color: Gray;
    }
    
    a.pagenav:visited {
    	color: #8F8080;
    }
    
    a.pagenav:hover {
    	color: Black;
    }
    
    p.snippet {
    	margin: 0.5em 0em;
    	font-family: monospace;
    	position: relative;
    	white-space: nowrap;
    }
    
    span.highlight {
    	background: #FFECC9;
    }
    
    input#q {
    	width: 250px;
    }
    
    input#fq {
    	width: 250px;
    }
    
    label[for="fq"] {
    	margin: 0em 0em 0em 0.5em;
    }
    
    input[type="submit"] {
    	margin: 0em 0em 0em 0.5em;
    }
    
    .facetlist li {
    	display: inline;
    	padding: 0.5em 0.5em;
    }
    
    .facetlist li.facetvalid {
    	background: #FFF4E0;
    }
    
    .facetlist li a.facet {
    	color: Black;
    }
    
    .facetlist li a.facet:hover {
    	color: #444;
    }
    
    div#yearbarchart {
      font: 10px sans-serif;
		}
		
		h3#resultsFound {
			margin: 2em 0em 0em 0em;
			color: #555;
		}
		
	  /* Kuler: Sweet reunion by kristi
	  	394230 dark green
	  	828130 med green
	  	BFBA68 light green
	  	FFECC9 tan
	  	BF9797 mauve
	  */
		.rule line {
			stroke: #eee;
			shape-rendering: crispEdges;
		}
		
		.rule line.axis {
			stroke: #000;
		}
		
		.yearrange line {
			stroke: #BF9797;
			stroke-width: 2px;
			shape-rendering: crispEdges;
		}
		
		.area {
			fill: #BFBA68;
		}
		
		.line, circle.area {
			fill: none;
			stroke: #828130;
			stroke-width: 1.5px;
		}
		
		circle.area {
			fill: #fff;
		}
        
		#testwidth {
			position: absolute;
			visibility: hidden;
			height: auto;
			width: auto;
		}

    </style>
  </head>
  <body>
    <form  accept-charset="utf-8" method="get">
      <label for="q">Search:</label>
      <input id="q" name="q" type="text" value="<?php echo htmlspecialchars($query, ENT_QUOTES, 'utf-8'); ?>"/>
      <label for="fq">pre-filter:</label>
      <input id="fq" name="fq" type="text" value="<?php echo htmlspecialchars($filter, ENT_QUOTES, 'utf-8'); ?>"/>
      <input id="min_ct" name="min_ct" type="hidden" value="<?php echo $min_ct; ?>"/>
      <input type="submit"/>
    </form>
    
<?php

// display results
if ($results)
{
  $total = (int) $results->response->numFound;
  $totalpages = ceil($total / $casesperpage);		// 1-based
  $start = (int) $results->response->start;
  $currentpage = (int) ($start / $casesperpage) + 1;	// 1-based
  $end = min($start+$casesperpage, $total);
  $q_str = htmlspecialchars($results->responseHeader->params->q, ENT_QUOTES, 'utf-8');
  $fq_str = htmlspecialchars($results->responseHeader->params->fq[1], ENT_QUOTES, 'utf-8');
  $start_year = 0;
  $current_year = 0;
  
  // Make sure can't inject bad $start value and get bad $currentpage
	if ($currentpage > $totalpages) 
	{
    $currentpage = $totalpages;
	}
	if ($currentpage < 1)
	{
    $currentpage = 1;
	}

  // Convert data format for use in d3 charts
  $year_facets = array();
  foreach ($results->facet_counts->facet_fields->year as $yr=>$yr_count)
  {
  	$year_facets[] = array('x'=>intval($yr), 'y'=>$yr_count );
  }
  
  // Convert format
  // and create facet links list
  $court_facets = array();
  echo '<ul class="facetlist">';
  // echo '<li>Courts: </li>';
  foreach ($results->facet_counts->facet_fields->court_level as $crt=>$crt_count)
  {
  	if ($crt > 0)
  	{
  	  $court_facets[] = array('x'=>intval($crt), 'y'=>$crt_count );
  	  if ($crt == 5) {
  	  	$crt_name = 'SCOTUS';
  	  } elseif ($crt == 4) {
  	  	$crt_name = 'US Appeals';
  	  } elseif ($crt == 3) {
  	  	$crt_name = 'US Dist';
  	  } elseif ($crt == 2) {
  	  	$crt_name = 'State';
  	  } else {
  	  	$crt_name = 'none';
  	  }
  	  $liclass = $crt >= $min_ct ? ' class="facetvalid"' : '';
  	  echo '<li'.$liclass.'><a class="facet" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$start.'&min_ct='.$crt.'">'.$crt_name.' ('.$crt_count.')</a></li>';
  	}
  }
  echo '</ul>';

  // Convert format
  // and create facet links list
  $tag_facets = array();
  echo '<ul class="facetlist">';
  // echo '<li>Tags: </li>';
  foreach ($results->facet_counts->facet_fields->tags as $tag=>$tag_count)
  {
  	echo '<li><a class="facet" >'.$tag.' ('.$tag_count.')</a></li>';
  }
  echo '</ul>';
  echo '<ul class="facetlist">';
  // echo '<li>Tags: </li>';
  foreach ($results->facet_counts->facet_fields->subjects as $tag=>$tag_count)
  {
  	echo '<li><a class="facet" >'.$tag.' ('.$tag_count.')</a></li>';
  }
  echo '</ul>';
?>

<!-- This used for testing snippet paragraph widths (not visible) -->
<div id="testwidth"></div>

<!-- Cases count per year graph will go here -->
<div id="yearbarchart" ></div>

<script type="text/javascript">
	
// If javascript enabled, then take monospaced out of line style
// There should only be one style sheet for now
// var ss = d3.selectAll('style').property('sheet').cssRules; 	// alternate access method...
var ss = document.styleSheets[0].cssRules;
for (var i=0; i < ss.length; i++) {
	if (ss.item(i).selectorText == "p.snippet") {
		ss.item(i).style.removeProperty("font-family");
		ss.item(i).style.setProperty("font-size", "90%", "")
	}
}
	
// Chart of counts per year	
var data = <?php echo json_encode($year_facets); ?>;
var court_data = <?php echo json_encode($court_facets); ?>;
	
var w = 750,
    cw = 100,
    h = 100,
    p = 20,
    xmin = d3.min(data, function(d) { return d.x; }),
    xmax = d3.max(data, function(d) { return d.x; }),
    ymin = d3.min(data, function(d) { return d.y; }),
    ymax = d3.max(data, function(d) { return d.y; }),
    cmax = d3.max(court_data, function(d) { return d.y; }),
    x = d3.scale.linear().domain([xmin, xmax]).range([0, w]),
    y = d3.scale.linear().domain([ymin, ymax]).range([h, 0]);
//     c = d3.scale.linear().domain([0, cmax]).range([0, x(1910)]),
//     l = d3.scale.linear().domain([2, 5]).range([h, 0]);

var vis = d3.select("div#yearbarchart")
  .append("svg")
    .data([data])
    .attr("width", w + p * 2)
    .attr("height", h + p * 2)
  .append("g")
    .attr("transform", "translate(" + p + "," + p + ")")
    .attr("class","main");
    
// var court_vis = vis.selectAll("g.c")
//     .data([court_data])
//     .enter().append("g")
//     .attr("class","courtbars");

var xrules = vis.selectAll("g.x")
    .data(x.ticks(10))
  .enter().append("g")
    .attr("class", "rule");

var yrules = vis.selectAll("g.y")
    .data(y.ticks(4))
  .enter().append("g")
    .attr("class", "rule");

xrules.append("line")
    .attr("x1", x)
    .attr("x2", x)
    .attr("y1", 0)
    .attr("y2", h - 1);

yrules.append("line")
    .attr("class", function(d) { return d==ymin ? "axis" : null; })
    .attr("y1", y)
    .attr("y2", y)
    .attr("x1", 0)
    .attr("x2", w + 1);

xrules.append("text")
    .attr("x", x)
    .attr("y", h + 3)
    .attr("dy", ".71em")
    .attr("text-anchor", "middle")
    .text(d3.format("g"));

yrules.append("text")
    .attr("y", y)
    .attr("x", -3)
    .attr("dy", ".35em")
    .attr("text-anchor", "end")
    .style("visibility", function(d) { return d==ymin ? "hidden" : "visible"; })
    .text(y.tickFormat(10));

vis.append("path")
    .attr("class", "area")
    .attr("d", d3.svg.area()
    .x(function(d) { return x(d.x); })
    .y0(h - 1)
    .y1(function(d) { return y(d.y); }));

vis.append("path")
    .attr("class", "line")
    .attr("d", d3.svg.line()
    .x(function(d) { return x(d.x); })
    .y(function(d) { return y(d.y); }));
    
// court_vis.append("path")
//     .attr("class", "line")
//     .attr("d", d3.svg.line()
//     .x(function(d) { return c(d.y); })
//     .y(function(d) { return l(d.x); }));

</script>

<?php

  // Page navigation links

  echo '<h3 id="resultsFound">Results: '.$start.' - '.$end.' of '.$total.' cases:</h3>';

  // Following http://www.phpfreaks.com/tutorial/basic-pagination
  
  if ($currentpage > 1)
  {
    echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start=0&min_ct='.$min_ct.'" ><<</a>&nbsp;';
    $new_start = ($currentpage - 2) * $casesperpage;
    echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" ><</a>&nbsp;';
  }
  
  // range of num links to show
	$navrange = 3;
	
	// loop to show links to range of pages around current page
	for ($x = ($currentpage - $navrange); $x < (($currentpage + $navrange)  + 1); $x++)
	{
		 if (($x > 0) && ($x <= $totalpages))
		 {
				if ($x == $currentpage)
				{
					 echo '<a class="pagenav">['.$x.']</a>&nbsp;';
				} 
				else
				{
					 $new_start = ($x - 1) * $casesperpage;
					 echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >'.strval($x).'</a>&nbsp;';
				}
		 } 
	}
  
  // if not on last page, show forward and last page links        
	if ($currentpage != $totalpages)
	{
		$nextpage = $currentpage + 1;
		$new_start = ($nextpage - 1) * $casesperpage;
		echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >></a>&nbsp;';
		$new_start = ($totalpages - 1) * $casesperpage;
		echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >>></a>';
	}
	


	// Iterate result documents
  foreach ($results->response->docs as $doc)
  {
  	if ($start_year == 0)
  	{
  		$start_year = $doc->year;
  	}
		$doc_id = $doc->_id;
		if ($doc->year !== $current_year)
		{
			$current_year = $doc->year;
			echo '<h2>'.$doc->year.'</h2>';
		}
		
		// Going to just note the first character of any tags present for now...
		$tag_str = "";
		if (is_string($doc->tags))
		{
		  $tag_str = substr($doc->tags, 0, 1);
		}
		if (is_array($doc->tags))
		{
			foreach ($doc->tags as $tmptag)
			{
			  if (is_string($tmptag))
			  {
			    $tag_str .= substr($tmptag, 0, 1);
			  }
			}
		}
		
		// Concatenate list of subjects
		$subj_str = "";
		if (is_string($doc->subjects))
		{
		  $subj_str = ' - ' . $doc->subjects;
		}
		if (is_array($doc->subjects))
		{
			$subj_str .= ' - ';
			foreach ($doc->subjects as $tmpsub)
			{
			  if (is_string($tmpsub))
			  {
			    $subj_str .= $tmpsub . ' ';
			  }
			}
		}		
		
		// Title
    echo '<h3>';
		if ($doc->court_level == 5) {
			$crt_name = 'SCOTUS';
		} elseif ($doc->court_level == 4) {
			$crt_name = 'US Appeals';
		} elseif ($doc->court_level == 3) {
			$crt_name = 'US Dist';
		} elseif ($doc->court_level == 2) {
			$crt_name = 'State';
		} else {
			$crt_name = 'none';
		}
    echo '<a href="http://'.$doc->url.'">'.htmlspecialchars(substr($doc->name,0,80), ENT_NOQUOTES, 'utf-8').'<br />('.$crt_name.' '.$tag_str.$subj_str.')</a>';
    echo '</h3>';
    
    // Snippets
    // NOTE: Sometimes we get matches but no highlighting content returned...
    if (array_key_exists('content', $results->highlighting->$doc_id))
    {
			foreach ($results->highlighting->$doc_id->content as $snippet)
			{
				$new_snip = stripslashes(trim($snippet));
				$new_snip = str_replace("\n", " ", $new_snip);
				// $new_spl = explode("<span", $new_snip);
				// $hi_offset = strlen($new_spl[0]);
				$hi_offset = stripos($new_snip, "<span");
				$left_pos = 40.7853 - 0.615635*$hi_offset;
				
				echo '<p class="snippet" style="left: '.$left_pos.'em" >'.$new_snip.'</p>';
			}
    }
  }
?>

<script type="text/javascript">

var year0 = <?php echo $start_year; ?>;
    year1 = <?php echo $current_year; ?>;
		
// Put indicator of year range on year histogram plot
// Using insert to put this line behind axis elements
var yearband = d3.select("g.main")
		.insert("g","g.rule")
    .attr("class", "yearrange");

yearband.append("line")
    .attr("x1", x(year0))
    .attr("x2", x(year1))
    .attr("y1", h+1)
    .attr("y2", h+1);


// Shift over all paragraphs using javascript instead so don't need monospaced font

// Method for text width calculation By CMPalmer
// http://stackoverflow.com/questions/118241/calculate-text-width-with-javascript
var test = document.getElementById("testwidth");

var measure_pre = function(pp) {
	test.innerHTML = '<p class="snippet">' + pp.innerHTML.split("<span")[0] + '</p>';
	return 500 - test.clientWidth;
}

var ps = d3.selectAll("p.snippet")
				.data(function() {return this.map(measure_pre);})
				.style("left", function(d) { return d + "px"; })
				.on("click", wrap_toggle);

function wrap_toggle(d, i) {
	tmp = this;
	if (this.getAttribute('style').indexOf('left: 0px') >= 0) {
  d3.select(this).transition()
  		.duration(400)
      .style("white-space", "nowrap")
      .style("left", function(d) { return d + "px"; });
	} else {
  d3.select(this).transition()
  		.duration(400)
      .style("white-space", "normal")
      .style("left", "0px");
	}
}

</script>
	
<?php

  // Page navigation links

  echo '<h3 id="resultsFound">Results: '.$start.' - '.$end.' of '.$total.' cases:</h3>';

  // Following http://www.phpfreaks.com/tutorial/basic-pagination
  
  if ($currentpage > 1)
  {
    echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start=0&min_ct='.$min_ct.'" ><<</a>&nbsp;';
    $new_start = ($currentpage - 2) * $casesperpage;
    echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" ><</a>&nbsp;';
  }
  
  // range of num links to show
	$navrange = 3;
	
	// loop to show links to range of pages around current page
	for ($x = ($currentpage - $navrange); $x < (($currentpage + $navrange)  + 1); $x++)
	{
		 if (($x > 0) && ($x <= $totalpages))
		 {
				if ($x == $currentpage)
				{
					 echo '<a class="pagenav">['.$x.']</a>&nbsp;';
				} 
				else
				{
					 $new_start = ($x - 1) * $casesperpage;
					 echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >'.strval($x).'</a>&nbsp;';
				}
		 } 
	}
  
  // if not on last page, show forward and last page links        
	if ($currentpage != $totalpages)
	{
		$nextpage = $currentpage + 1;
		$new_start = ($nextpage - 1) * $casesperpage;
		echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >></a>&nbsp;';
		$new_start = ($totalpages - 1) * $casesperpage;
		echo '<a class="pagenav" href="'.$_SERVER['PHP_SELF'].'?q='.$q_str.'&fq='.$fq_str.'&start='.$new_start.'&min_ct='.$min_ct.'" >>></a>';
	}
	  
} // if ($results)
?>

  </body>
</html>