// Draws one data set with Plotly

window.BeamdbPlot = (function () {

    // log axis cannot take zero or negative
    function positive(value) {
        return (value === null || value === undefined || value <= 0) ? null : value;
    }

    function scale(row, log) {
        return row.map(function (value) { return log ? positive(value) : value; });
    }

    function is3d(data) {
        return data.kind === 'surface' || data.kind === 'waterfall';
    }

    // how many decades the values span, so wide ranges get fewer labels
    function decades(data) {
        var low = Infinity, high = -Infinity;
        var rows = data.z ? data.z : data.series.map(function (s) { return s.y; });
        rows.forEach(function (row) {
            row.forEach(function (value) {
                if (value > 0) {
                    if (value < low) low = value;
                    if (value > high) high = value;
                }
            });
        });
        return low === Infinity ? 1 : Math.log10(high) - Math.log10(low);
    }

    function valueAxis(data, log) {
        var axis = {title: data.cs_type + '<br>[' + data.unit_y + ']',
                    type: log ? 'log' : 'linear',
                    exponentformat: 'power'};
        // labels every one, two or three decades, so they never run into the title
        if (log) axis.dtick = Math.max(1, Math.ceil(decades(data) / 4));
        else axis.nticks = 5;
        return axis;
    }

    function hoverTemplate(data) {
        return 'theta = %{x}' + data.unit_angle + '<br>E = %{y}' + data.unit_energy +
               '<br>' + data.cs_type + ' = %{z:.3e}<extra></extra>';
    }

    function surfaceTrace(data, log) {
        var z = data.z.map(function (row) { return scale(row, log); });
        return [{
            type: 'surface',
            x: data.angles,
            y: data.energies,
            z: z,
            // colour follows the log height
            surfacecolor: log ? z.map(function (row) {
                return row.map(function (value) {
                    return value === null ? null : Math.log10(value);
                });
            }) : z,
            colorscale: 'Viridis',
            colorbar: {title: log ? 'log10 ' + data.unit_y : data.unit_y,
                       titleside: 'right', exponentformat: 'power'},
            hovertemplate: hoverTemplate(data),
            contours: {z: {show: true, usecolormap: true, project: {z: true}}}
        }];
    }

    function waterfallTraces(data, log) {
        return data.series.map(function (series) {
            return {
                type: 'scatter3d',
                mode: 'lines+markers',
                name: series.energy + ' ' + data.unit_energy,
                x: series.angle,
                y: series.angle.map(function () { return series.energy; }),
                z: scale(series.y, log),
                line: {width: 4},
                marker: {size: 3},
                hovertemplate: hoverTemplate(data)
            };
        });
    }

    function curveTraces(data, log) {
        if (data.kind === 'curve_e') {
            var series = data.series[0];
            return [{
                type: 'scatter',
                mode: 'lines+markers',
                name: data.cs_type,
                x: series.x,
                y: scale(series.y, log),
                error_y: {type: 'data', array: series.error, visible: true}
            }];
        }
        return data.series.map(function (series) {
            return {
                type: 'scatter',
                mode: 'lines+markers',
                name: series.energy + ' ' + data.unit_energy,
                x: series.angle,
                y: scale(series.y, log),
                error_y: {type: 'data', array: series.error, visible: true}
            };
        });
    }

    function layout(data, mode, log) {
        if (mode === '3d') {
            return {
                font: {size: 14},
                margin: {l: 0, r: 0, t: 10, b: 0},
                scene: {xaxis: {title: 'theta<br>[' + data.unit_angle + ']', nticks: 4},
                        yaxis: {title: 'E<br>[' + data.unit_energy + ']', nticks: 4},
                        zaxis: valueAxis(data, log),
                        camera: {eye: {x: 1.7, y: -1.6, z: 0.9}}},
                showlegend: data.kind !== 'surface'
            };
        }
        if (data.kind === 'curve_e') {
            return {
                font: {size: 14},
                margin: {l: 85, r: 20, t: 20, b: 55},
                xaxis: {title: 'E [' + data.unit_energy + ']', type: 'log',
                        exponentformat: 'power', dtick: 1},
                yaxis: valueAxis(data, log)
            };
        }
        return {
            font: {size: 14},
            margin: {l: 85, r: 20, t: 20, b: 55},
            xaxis: {title: 'theta [' + data.unit_angle + ']'},
            yaxis: valueAxis(data, log),
            legend: {title: {text: 'E [' + data.unit_energy + ']'}}
        };
    }

    function traces(data, mode, log) {
        if (mode === '3d' && data.kind === 'surface') return surfaceTrace(data, log);
        if (mode === '3d') return waterfallTraces(data, log);
        return curveTraces(data, log);
    }

    function draw(element, data, options) {
        options = options || {};
        var mode = options.mode || (is3d(data) ? '3d' : '2d');
        var log = options.log === undefined ? true : options.log;

        if (data.kind === 'invalid') {
            element.innerHTML = '<p class="message">This set cannot be plotted: ' +
                                (data.problems || []).join('; ') + '</p>';
            return;
        }
        Plotly.react(element, traces(data, mode, log), layout(data, mode, log),
                     {responsive: true, displaylogo: false,
                      toImageButtonOptions: {filename: 'ipbdb-' + data.id, scale: 2}});
    }

    return {draw: draw, is3d: is3d};
})();
