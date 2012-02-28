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
  'facet.limit' => '1000',
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
    
    label {
    	font-size: 80%;
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
    
    /* don't need monospace font if javascript enabled */
    p.snippetJS {
    	margin: 0.5em 0em;
    	font-size: 90%;
    	position: relative;
    	white-space: nowrap;
    }
    
    span.highlight {
    	background: #FFB;
    }
    
    input#q {
    	width: 250px;
    }
    
    div#yearbarchart {
      font: 10px sans-serif;
		}
		
		h3#resultsFound {
			margin: 2em 0em 0em 0em;
			color: #555;
		}
		
		.rule line {
			stroke: #eee;
			shape-rendering: crispEdges;
		}
		
		.rule line.axis {
			stroke: #000;
		}
		
		.area {
			fill: lightsteelblue;
		}
		
		.line, circle.area {
			fill: none;
			stroke: steelblue;
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
      <input type="submit"/>
    </form>
    <div id="testwidth"></div>
    <div id="yearbarchart" ></div>
<?php

// display results
if ($results)
{
  $total = (int) $results->response->numFound;
  $start = min(1, $total);
  $end = min($limit, $total);
  $current_year = 0;
  
  // Convert data format for use in d3 chart
  $year_facets = array();
  foreach ($results->facet_counts->facet_fields->year as $yr=>$yr_count)
  {
  	$year_facets[] = array('x'=>intval($yr), 'y'=>$yr_count );
  }
?>
    <h3 id="resultsFound">Results <?php echo $start; ?> - <?php echo $end;?> of <?php echo $total; ?>:</h3>
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
?>
<p class="snippetJS" style="left: 0px" ><?php echo $snippet; ?></p>
<?php
    }
  }
}
?>
	<script type="text/javascript">
	
var data = <?php echo json_encode($year_facets); ?>;
	
var w = 750,
    h = 100,
    p = 20,
    xmin = d3.min(data, function(d) { return d.x; }),
    xmax = d3.max(data, function(d) { return d.x; }),
    ymin = d3.min(data, function(d) { return d.y; }),
    ymax = d3.max(data, function(d) { return d.y; }),
    x = d3.scale.linear().domain([xmin, xmax]).range([0, w]),
    y = d3.scale.linear().domain([ymin, ymax]).range([h, 0]);

var vis = d3.select("div#yearbarchart")
  .append("svg")
    .data([data])
    .attr("width", w + p * 2)
    .attr("height", h + p * 2)
  .append("g")
    .attr("transform", "translate(" + p + "," + p + ")");

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

// Shift over all paragraphs using javascript instead so don't need monospaced font

// Method for text width calculation By CMPalmer
// http://stackoverflow.com/questions/118241/calculate-text-width-with-javascript
var test = document.getElementById("testwidth");

var measure_pre = function(pp) {
	test.innerHTML = '<p class="snippetJS">' + pp.innerHTML.split("<span")[0] + '</p>';
	return 500 - test.clientWidth;
}

var ps = d3.selectAll("p.snippetJS")
				.data(function() {return this.map(measure_pre);})
				.style("left", function(d) { return d + "px"; })
				.on("click", wrap_toggle);

var tmp = null;

function wrap_toggle(d, i) {
	tmp = this;
	if (this.getAttribute('style').indexOf('left: 0px') >= 0) {
  d3.select(this).transition()
  		.duration(200)
      .style("white-space", "nowrap")
      .style("left", function(d) { return d + "px"; });
	} else {
  d3.select(this).transition()
  		.duration(200)
      .style("white-space", "normal")
      .style("left", "0px");
	}
}

	</script>
  </body>
</html>