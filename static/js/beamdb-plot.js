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

    function valueAxis(data, log, oneLine) {
        // a scene draws the second line of a title over the numbers, so 3d gets one line
        var axis = {title: data.cs_type + (oneLine ? ' [' : '<br>[') + data.unit_y + ']',
                    type: log ? 'log' : 'linear',
                    exponentformat: 'power'};
        // labels every one, two or three decades, so they never run into the title
        if (log) axis.dtick = Math.max(1, Math.ceil(decades(data) / 4));
        else axis.nticks = 5;
        return axis;
    }

    // the three axes of a scene share their look
    function sceneAxis(axis, nticks) {
        axis.titlefont = {size: 13};
        axis.tickfont = {size: 11};
        axis.gridcolor = '#dddddd';
        axis.zerolinecolor = '#cccccc';
        axis.backgroundcolor = '#fbfbfb';
        axis.showbackground = true;
        if (nticks) axis.nticks = nticks;
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
            colorbar: {title: {text: log ? 'log10 ' + data.unit_y : data.unit_y,
                               side: 'right', font: {size: 12}},
                       tickfont: {size: 11}, thickness: 14, len: 0.7,
                       exponentformat: 'power'},
            hovertemplate: hoverTemplate(data),
            contours: {z: {show: true, usecolormap: true, project: {z: true}}}
        }];
    }

    function waterfallTraces(data, log) {
        return data.series.map(function (series) {
            return {
                type: 'scatter3d',
                mode: 'lines+markers',
                name: String(series.energy),
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
                line: {shape: 'spline', smoothing: 0.8},
                x: series.x,
                y: scale(series.y, log),
                error_y: {type: 'data', array: series.error, visible: true}
            }];
        }
        return data.series.map(function (series) {
            return {
                type: 'scatter',
                mode: 'lines+markers',
                name: String(series.energy),
                line: {shape: 'spline', smoothing: 0.8},
                x: series.angle,
                y: scale(series.y, log),
                error_y: {type: 'data', array: series.error, visible: true}
            };
        });
    }

    function flatLayout(data, log, xaxis, legendTitle) {
        var out = {font: {size: 14},
                   margin: {l: 95, r: 20, t: 20, b: 55},
                   xaxis: xaxis,
                   yaxis: valueAxis(data, log)};
        if (legendTitle) out.legend = {title: {text: legendTitle}};
        return out;
    }

    function layout(data, mode, log) {
        if (mode === '3d') {
            return {
                font: {size: 13},
                margin: {l: 0, r: 0, t: 0, b: 0},
                scene: {
                    xaxis: sceneAxis({title: 'theta [' + data.unit_angle + ']'}, 5),
                    yaxis: sceneAxis({title: data.energy_label + ' [' +
                                             data.unit_energy + ']'}, 5),
                    zaxis: sceneAxis(valueAxis(data, log, true)),
                    aspectmode: 'manual',
                    aspectratio: {x: 1.15, y: 1.15, z: 0.9},
                    // far enough back that the titles clear the numbers
                    camera: {eye: {x: 1.8, y: -1.7, z: 0.75},
                             center: {x: 0, y: 0, z: -0.12}}
                },
                showlegend: data.kind !== 'surface',
                legend: {font: {size: 11}, itemsizing: 'constant',
                         title: {text: data.energy_label + ' [' +
                                       data.unit_energy + ']', font: {size: 11}}}
            };
        }
        if (data.kind === 'curve_e') {
            var x = data.series[0].x.filter(function (v) { return v > 0; });
            // a log axis only pays off when the energies span more than a decade
            var wide = x.length && Math.log10(Math.max.apply(null, x)) -
                                   Math.log10(Math.min.apply(null, x)) > 1.5;
            var xaxis = {title: data.energy_label + ' [' + data.unit_energy + ']'};
            if (wide) {
                xaxis.type = 'log';
                xaxis.exponentformat = 'power';
                xaxis.dtick = 1;
            }
            return flatLayout(data, log, xaxis);
        }
        return flatLayout(data, log, {title: 'theta [' + data.unit_angle + ']'},
                          'E [' + data.unit_energy + ']');
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
