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
  'fl' => '_id,url,year,name,score,court_level,tags',
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
        'tags'
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
    <title>Solr Word Tree</title>
    <script type="text/javascript" src="d3.v2.js"></script>
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
    	width: 150px;
    }
    
    label[for="fq"] {
    	margin: 0em 0em 0em 0.5em;
    }
    
    input[type="submit"] {
    	margin: 0em 0em 0em 0.5em;
    }
    
    .facetlist li {
    	display: inline;
    	padding: 0.5em 1em;
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
		
		/* word tree */
		.link {
			fill: none;
			stroke: #c69547;
			stroke-width: 1px;
		}
		
		g {
			background-color: black;
		}
		
		g text {
			font-family: sans-serif;
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
?>

<!-- This used for testing snippet paragraph widths (not visible) -->
<div id="testwidth"></div>

<!-- Invisible SVG for measuring text will go here -->
<div id="inviz"></div>

<!-- Cases count per year graph will go here -->
<div id="viz"></div>


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
	
</script>

<?php
	// Iterate result documents to gather up snippet paragraphs for javascript analysis
  $snippet_paras = array();
  foreach ($results->response->docs as $doc)
  {
		$doc_id = $doc->_id;
    // Snippets
    // NOTE: Sometimes we get matches but no highlighting content returned...
    if (array_key_exists('content', $results->highlighting->$doc_id))
    {
			foreach ($results->highlighting->$doc_id->content as $snippet)
			{
				$new_snip = stripslashes(trim($snippet));
				$new_snip = str_replace("\n", " ", $new_snip);
				
				// memory-wasteful, but flexible and generic...
				$snippet_paras[] = array('para'=>$new_snip, 'year'=>$doc->year, 'url'=>$doc->url );
			}
    }
  }
?>

<script type="text/javascript">

var snippets = <?php echo json_encode($snippet_paras); ?>;

// WORD TREE

// Loop through paragraphs to build word tree(s)
var wholeTree = {},
    para_spans = '',
    term_idx = -1,
    para_text = '',
    para_sub = '',
    tok = '',
    para_tokens = []
    jc = 0,
    parent_node = null,
    children_node = null;

wholeTree.name = 'root';
wholeTree.children = {};
wholeTree.child_names = [];

for (var i = 0; i < snippets.length; i++) {
	tmp = snippets[i].para;
	para = document.createElement('p');
	para.innerHTML = tmp;
	para_spans = para.getElementsByTagName('span');
	para_text = para.textContent;
	// NOTE: This is only grabbing first instance of single term!!!!
	para_sub = para_text.substring(para_text.indexOf(para_spans[0].textContent));
	// tokenize paragraph text. Need to find another way that preserves punctuation...
	para_tokens = para_sub.toLowerCase().split(/[^a-zA-Z0-9]/);
	parent_node = wholeTree;
	children_node = wholeTree.children;
	jc = 0;
	for (var j = 0; j < para_tokens.length; j++) {
	  tok = para_tokens[j];
		if (tok !== "") {
			if (!children_node.hasOwnProperty(tok)) {
				parent_node.child_names.push(tok);
				children_node[tok] = {};
				children_node[tok].name = tok;
				children_node[tok].count = 0;
				children_node[tok].years = [];
				children_node[tok].children = {};
				children_node[tok].child_names = [];
			}
			parent_node = children_node[tok];
			parent_node.count += 1;
			children_node = parent_node.children;
			jc++;
			// Temporary depth limiter
			// NOTE: Should have entries for long strings after certain depth...
			//  and maybe also a terminating leaf character or flag...
			if (jc > 12) {
				break;
			}
		}
	}
}

// Convert data over to tree format needed for vis
function add_children(orig, dest) {
	dest.name = orig.name;
	var term;
	for (var i = 0; i < orig.child_names.length; i++) {
		if (i === 0) {
			dest.children = [];
		}
		term = orig.child_names[i];
		dest.children.push({'name':term, 'count':orig.children[term].count});
		if (orig.children[term].child_names.length > 0) {
			add_children(orig.children[term], dest.children[i]);
		}
	}
}

// Need a round of cleanup where single children lines are strung together into
// concatenated strings
function append_single_children(node) {
  for (var n = 0; n < node.child_names.length; n++) {
  	var far_enough = false;
  	while (far_enough === false) {
			var childname = node.child_names[n];
			var child = node.children[childname];
			if (child.child_names.length === 1) {
				var grandchildname = child.child_names[0];
				var newchildname = childname + ' ' + grandchildname;
				// update current node children and child names
				node.child_names[n] = newchildname;
				node.children[newchildname] = child.children[grandchildname];
				node.children[newchildname].name = newchildname;
				delete node.children[child];
			}
			else {
			  far_enough = true;
			  append_single_children(child);
			}
    }
  }
}

append_single_children(wholeTree);

var treeData = {};
treeData.count = 1;
add_children(wholeTree, treeData);
// console.log(JSON.stringify(treeData,null,'  '));

// Vis based on:
// http://javadude.wordpress.com/2011/10/27/d3-js-tree-most-simple-sample/
// http://bl.ocks.org/1312406

var vis = d3.select("#inviz").append("svg:svg")
    .attr("width", 1)
    .attr("height", 1)
  .append("svg:g")
    .attr("transform", "translate(40, 0)");

// This has all of the real layout stripped away, but still
// generates the hierarchy list
var tree = d3.layout.tree_tw();

// Using custom diagonal calculator which adds in parentwidths
var diagonal = d3.svg.diagonal_tw()
  .projection(function(d) { return [d.y, d.x]; });

var nodes = tree.nodes(treeData);

var max_count = d3.max(nodes, function(d) { return d.count; }),
    font_scale = d3.scale.linear().domain([0, Math.sqrt(max_count)]).range([0, 40]);

// This tree of words isn't displayed, but used to calculate text offsets
var inode = vis.selectAll("g.node")
    .data(nodes)
  .enter().append("svg:g")
  	.attr("display", "none")
    .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

inode.append("svg:text")
    .attr("font-size", function(d) { return font_scale(Math.sqrt(d.count)); })
    .attr("text-anchor", "start" )
    .attr("baseline-shift", "-25%")
    .text(function(d) { return d.name; });

// grab text bbox width and set as part of original nodes data
// All layout algorithms assume top to bottom layout, so need to swap
// width and height of text to pretend it's hanging down...
inode.datum(function(d){
    d.height = this.lastChild.getBBox().width;
    d.width = this.lastChild.getBBox().height;
    return d; });

var leftmost = 0,
        gap = 0,
        edge = 50;

function postorder(node) {
	if (!node.parent) {
		node.parentheights = 0;
	}
	if (!node.width) {
		node.width = 0;
	}
	if (!node.height) {
		node.height = 0;
	}
	if (node.children && (node.children.length > 0)) {
		var childxsum = 0;
		var child = null;
		for (var j = 0; j < node.children.length; j++) {
			child = node.children[j];
			child.parentheights = node.parentheights + node.height;
			postorder(child);
			childxsum = childxsum + child.x;
		}
		node.x = childxsum / node.children.length;
	}
	else {
		node.x = leftmost + gap;
		leftmost = node.x + node.width;
	}
	node.y = node.depth*edge + node.parentheights;
}

// Compute the layout.
postorder(nodes[0]);


// Real visible tree
var vis = d3.select("#viz").append("svg:svg")
    .attr("width", 1000)
    .attr("height", 1600)
  .append("svg:g")
    .attr("transform", "translate(40, 0)");

var node = vis.selectAll("g.node")
    .data(nodes.slice(1))
  .enter().append("svg:g")
    .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

node.append("svg:text")
    .attr("font-size", function(d) { return font_scale(Math.sqrt(d.count)); })
    .attr("text-anchor", "start" )
    .attr("baseline-shift", "-25%")
    .attr("fill", function(d) { return d.count < 2 ? "gray" : "black"; } )
    .text(function(d) { return d.name; });

var link = vis.selectAll("pathlink")
    .data(tree.links(nodes.slice(1)))
  .enter().append("svg:path")
    .attr("class", "link")
    .attr("d", diagonal);



</script>
	
<?php
} // if ($results)
?>

  </body>
</html>