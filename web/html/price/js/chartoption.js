Highcharts.setOptions({
  global: {
    useUTC: false
  }
});

var draw= function(hashrate, doarate) {
  char= new Highcharts.stockChart({
    credits: { enabled: false },
    chart: { 
        renderTo: 'graph', 
        zoomType: 'x'
    },
    exporting: { enabled: false },
    title: { text: 'Dash price' },
    rangeSelector: {
        buttons: [{
            type: 'hour',
            count: 1,
            text: '1h'
        }, {
            type: 'day',
            count: 1,
            text: '1d'
        }, {
            type: 'month',
            count: 1,
            text: '1m'
        }, {
            type: 'year',
            count: 1,
            text: '1y'
        }, {
            type: 'all',
            text: 'All'
        }],
        inputEnabled: false, // it supports only days
        selected: 1 // all
    },
    xAxis: {
      type: 'datetime',
      dateTimeLabelFormats: {
        month: '%e. %b',
        year: '%b'
      },
      maxZoom: 12 * 3600,
      title: {
        text: null
      }
    },
    yAxis: [{
        //min: 0, 
            title: {
                text: 'USD'
            }
        }, {
            title: {
                text: 'BTC'
            },
        opposite: true
        }],
    tooltip: {
      shared: true
    },
    legend: {
      enabled: true,
      borderWidth: 0
    },
    plotOptions: {
      areaspline: {
        fillColor: '#ace',
        marker: { enabled: false },
        lineWidth: 1,
        shadow: false,
        states: {
          hover: { lineWidth: 1 }
        },
        threshold: null
      },
      spline: {
        marker: { enabled: false },
        lineWidth: 1,
        shadow: true,
        states: {
          hover: { lineWidth: 1 }
        },
        threshold: null
      },
    },
    series: [{
      type: 'areaspline',
      name: 'USD',
      data: hashrate,
      valueDecimals: 2,
      lineWidth: 2,
      marker: {
        enabled: false
      },
      yAxis: 0,
    },{
      type: 'spline',
      name: 'BTC',
      data: doarate,
      valueDecimals: 5,
      lineWidth: 1,
      marker: {
        enabled: false
      },
      color: '#761800',
      yAxis: 1
    }]
  });
};
