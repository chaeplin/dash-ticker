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
            count: 6,
            text: '6h'
        }, {
            type: 'day',
            count: 1,
            text: '1d'
        }, {
            type: 'day',
            count: 7,
            text: '7d'
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
        selected: 2 // all
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
          },
          showEmpty: false,
          height: '80%',
          opposite: true,
          floor: 0          
        }, {
        //min: 0,
        title: {
          text: 'BTC'
        },
          showEmpty: false,
          height: '80%',
          opposite: true,
          floor: 0
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
      tooltip: {
        valueDecimals: 2
      },
      lineWidth: 2,
      marker: {
        enabled: false
      },
      yAxis: 0,
    },{
      type: 'spline',
      name: 'BTC',
      data: doarate,
      tooltip: {
        valueDecimals: 5
      },
      lineWidth: 1,
      marker: {
        enabled: false
      },
      color: '#761800',
      yAxis: 1
    }]
  });
};
