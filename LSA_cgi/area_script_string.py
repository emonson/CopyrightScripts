def script_string():
  return """
<script type="text/javascript+protovis">

/* Sizing and scales. */
var w = 400,
    h = 200,
    x = pv.Scale.linear(data, function(d) d.x).range(0, w),
    y = pv.Scale.linear(0, 1).range(0, h);

/* The root panel. */
var vis = new pv.Panel()
    .width(w)
    .height(h)
    .bottom(20)
    .left(20)
    .right(10)
    .top(5);

/* Y-axis and ticks. */
vis.add(pv.Rule)
    .data(y.ticks(5))
    .bottom(y)
    .strokeStyle(function(d) d ? "#eee" : "#000")
  .anchor("left").add(pv.Label)
    .text(y.tickFormat);

/* X-axis and ticks. */
vis.add(pv.Rule)
    .data(x.ticks())
    .visible(function(d) d)
    .left(x)
    .bottom(-5)
    .height(5)
  .anchor("bottom").add(pv.Label)
    .text(x.tickFormat);

/* The area with top line. */
vis.add(pv.Area)
    .data(data)
    .bottom(1)
    .left(function(d) x(d.x))
    .height(function(d) y(d.y))
    .fillStyle("rgb(121,173,210)")
  .anchor("top").add(pv.Line)
    .lineWidth(3);

vis.render();

DATA_GOES_HERE

</script>"""