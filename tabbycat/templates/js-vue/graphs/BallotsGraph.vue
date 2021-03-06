<template id="ballots-graph">

  <svg id="ballotsStatusGraph" class="d3-graph" style="margin-top: -15px; margin-bottom: -15px;" width="100%"></svg>
  <div v-if="graphData.length === 0" class="text-center">No ballots in for this round yet</div>

</template>

<script>
var d3 = require("d3");

export default {
  props: {
    pollUrl: String,
    height: { type: Number, default: 200 },
    padding: { type: Number, default: 30 },
    pollFrequency: { type: Number, default: 30000 }, // 30s
    graphData: { type: Number,  default: function () { return [] } }
  },
  methods: {
    fetchData: function () {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', self.pollUrl)
      xhr.onload = function () {
        self.graphData = JSON.parse(xhr.responseText)
        if (self.graphData.length > 0) {
          initChart(self); // Don't init if no data is present
        }
        setTimeout(self.fetchData, self.pollFrequency);
      }
      xhr.send()
    }
  },
  created: function() {
    this.fetchData();
  },
}

function initChart(vueContext){

  // Responsive width
  vueContext.width = parseInt(d3.select('#ballotsStatusGraph').style('width'), 10)

  var x = d3.scale.ordinal().rangeRoundBands([0, vueContext.width])
  var y = d3.scale.linear().range([0, vueContext.height])
  var z = d3.scale.ordinal().range(["#e34e42", "#f0c230", "#43ca75"]) // red-orange-green

  d3.selectAll("svg > *").remove(); // Remove prior graph

  // Create Canvas and Scales
  var svg = d3.select("#ballotsStatusGraph")
    .attr("width", vueContext.width)
    .attr("height", vueContext.height + vueContext.padding + vueContext.padding)
    .append("g")
    .attr("transform", "translate(0," + (vueContext.height + vueContext.padding) + ")");

  // Data Transforms and Domains
  var matrix = vueContext.graphData; // 4 columns: time_ID,none,draft,confirmed
  var remapped =["c1","c2","c3"].map(function(dat,i){
      return matrix.map(function(d,ii){
          return {x: d[0], y: d[i+1] };
      })
  });
  var stacked = d3.layout.stack()(remapped)

  x.domain(stacked[0].map(function(d) { return d.x; }));
  y.domain([0, d3.max(stacked[stacked.length - 1], function(d) { return d.y0 + d.y; })]);

  // Add a group for each column.
  var valgroup = svg.selectAll("g.valgroup")
    .data(stacked)
    .enter().append("svg:g")
    .attr("class", "valgroup")
    .style("fill", function(d, i) { return z(i); })
    .style("stroke", "rgba(255,255,255,0.25)"); // Vertical Grid lines

  // Add a rect for each date.
  var rect = valgroup.selectAll("rect")
    .data(function(d){return d;})
    .enter().append("svg:rect")
    .attr("x", function(d) { return x(d.x); })
    .attr("y", function(d) { return -y(d.y0) - y(d.y); })
    .attr("height", function(d) { return y(d.y); })
    .attr("width", x.rangeBand());

  function formatTimeAgo(time) {
    if (time < 120) {
      // Less than two hours
      return "-" + time + "m";
    } else if (time < 2880) {
      // Less than 48 hours
      return "-" + Math.floor(time / 60) + "h";
    } else {
      // Greater than 48 hours
      return "-" + Math.floor(time / 24 / 60) + "d";
    }
  }

  // Add Scales
  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickFormat(function(d) { return formatTimeAgo(d) }) // Format result

  svg.append("g").attr("class", "x axis")
    .call(xAxis)

};

</script>