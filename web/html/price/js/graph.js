$(document).ready(function() {
  $(document).trigger('init');
});

// reload timers 
var intervalFigures = 60;
var intervalGraph = 600;

// array defining my addresses for highlighting them
var myself= [ ];

// ==================================================================
// custom event handlers

// init

$(document).on('init', function(e, eventInfo) {
  fetchGraph();
});

$(document).on('update', function(e, eventInfo) {
  fetchGraph();
});

var fetchGraph= function(interval) {
  var graph_hashrate= [], graph_doa_hashrate= [];


  $.getJSON('/data/v1/dashusd/avg?callback=?', function (data) {
    $.each(data, function(key, value) {
      el= []; el.push(parseInt(value[0]),
        parseFloat(value[1]));
      graph_hashrate.push(el);
    });
    graph_hashrate.sort();
    $.getJSON('/data/v1/dashbtc/avg?callback=?', function (data) {
      $.each(data, function(key, value) {
        el= []; el.push(parseInt(value[0]),
          parseFloat(value[1]));
        graph_doa_hashrate.push(el);
      });
      graph_doa_hashrate.sort();
      draw(graph_hashrate, graph_doa_hashrate, interval);
    })
  })
}


//setInterval(function() {
//  $(document).trigger('update');
//}, intervalFigures * 1000);














































