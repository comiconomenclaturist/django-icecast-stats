// Global ChartJS config
Chart.defaults.plugins.legend.position = 'right';
Chart.defaults.plugins.legend.display = false;
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.title.display = true;
Chart.defaults.plugins.title.font = {
    weight: 'normal',
    size: 13,
    family: "'Open Sans', sans-serif",
}
Chart.defaults.maintainAspectRatio = false;
Chart.defaults.color = 'lightgrey';
Chart.defaults.scale.grid.color = '#555';
Chart.defaults.scale.grid.borderColor = '#555';
Chart.defaults.scale.grid.drawOnChartArea = false;
Chart.defaults.scale.ticks.font = {
    size: 10,
}

var colours = ['#FF4E67', '#F77D50', '#EFBD52', '#DAE753', '#9ADF55', '#62D856', '#58D07E', '#59C9AB', '#5AB3C1']

// Callbacks for ChartJS tooltips
const labelColor = {
    labelColor: (context) => {
        return {
            borderColor: colours[context.datasetIndex],
            backgroundColor: colours[context.datasetIndex],
            borderWidth: 2,
        };
    },
}

const verticalChartCallbacks = {
    title: (context) => {
        times = new Set(context[0].dataset.data.map(function (e) {
            return e.x.toLocaleTimeString()
        }));
        if (times.size > 1) {
            return moment(context[0].raw.x).format('ddd Do MMM, YYYY – LT');
        } else {
            return moment(context[0].raw.x).format('ddd Do MMM, YYYY');
        }
    },
    afterLabel: (context) => {
        datasets = context.chart.data.datasets;
        window.total = datasets.reduce((sum, dataset) => {
            return sum + dataset.data[context.dataIndex].y
        }, 0)
    },
    footer: (context) => {
        return `Total: ${parseFloat(window.total.toFixed(2))}`;
    },
    ...labelColor,
}

const horizontalChartCallbacks = {
    afterLabel: (context) => {
        var val = parseFloat(context.dataset.data[context.dataIndex]);
        window.percentage = val / context.chart.data.total * 100;
    },
    footer: function () {
        return window.percentage.toFixed(2) + '% of total';
    }
}
