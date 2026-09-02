// Local combo-ajax.js, requests go to this node

$(document).ready(function () {

    var base_url = '';
    var colltypes = 'select[name=CollisionTypes]';
    var species = 'select[name=Species]';
    var states = 'select[name=SpeciesStates]';
    var cstypes = 'select[name=CrossSectionTypes]';

    $(colltypes + ' option:eq(0)').prop('selected', 'selected');
    $(species).resetElem();
    $(states).resetElem();
    $(cstypes).resetElem();

    $(colltypes).change(function () {
        var coll_type_id = $(this).val();
        $(species).resetElem();
        $(states).resetElem();
        $(cstypes).resetElem();
        if (!coll_type_id) return;
        $(species).removeAttr('disabled');
        $.getJSON(base_url + '/get_species/' + coll_type_id + '/', function (data) {
            $.each(data, function (key, value) {
                $(species).append('<option value="' + key + '">' + value + '</option>');
            });
        });
    });

    $(species).change(function () {
        var species_id = $(this).val();
        var coll_type_id = $(colltypes).val();
        $(states).resetElem();
        $(cstypes).resetElem();
        if (!species_id) return;
        $(states).removeAttr('disabled');
        $.getJSON(base_url + '/get_states/' + species_id + '/' + coll_type_id + '/', function (data) {
            $.each(data, function (key, value) {
                $(states).append('<option value="' + key + '">' + value + '</option>');
            });
        });
    });

    $(states).change(function () {
        var state_id = $(this).val();
        var coll_type_id = $(colltypes).val();
        $(cstypes).resetElem();
        if (!state_id) return;
        $(cstypes).removeAttr('disabled');
        $.getJSON(base_url + '/get_cs_types/' + state_id + '/' + coll_type_id + '/', function (data) {
            $.each(data, function (key, value) {
                $(cstypes).append('<option value="' + key + '">' + value + '</option>');
            });
        });
    });

    function escapeHtml(text) {
        return $('<div>').text(text === null || text === undefined ? '' : text).html();
    }

    function processCell(group) {
        return escapeHtml(group.target_formula || group.target) + ' + e&#8315; &rarr; ' +
               escapeHtml(group.product_formula || group.product) +
               (group.product_state ? ' (' + escapeHtml(group.product_state) + ')' : '') +
               '<br><small>' + escapeHtml(group.collision_type) + '</small>';
    }

    function linksCell(dataset) {
        if (dataset.kind === 'invalid') {
            return '<small>no plot</small>';
        }
        return '<a href="/plots/' + dataset.id + '/">plot</a> &middot; ' +
               '<a href="/plots/' + dataset.id + '/data.csv">CSV</a>';
    }

    function renderSummary(data) {
        if (!data.groups.length) {
            $('#summary').html('<p>No data for this query.</p>');
            $('#xmlbox').hide();
            return;
        }
        var html = '<div class="counts">Found <b>' + data.counts.collisions +
                   '</b> collisions, <b>' + data.counts.datasets + '</b> data sets, <b>' +
                   data.counts.sources + '</b> sources.</div>';
        html += '<table><tr><th>process</th><th>cross section</th>' +
                '<th>points</th><th>plot type</th><th></th></tr>';
        data.groups.forEach(function (group) {
            group.datasets.forEach(function (dataset) {
                var warning = dataset.problems.length
                    ? '<div class="warn">' + escapeHtml(dataset.problems.join('; ')) + '</div>'
                    : '';
                html += '<tr>' +
                        '<td>' + processCell(group) + '</td>' +
                        '<td>' + escapeHtml(dataset.cs_name) + ' (' + escapeHtml(dataset.cs_type) +
                        ')' + warning + '</td>' +
                        '<td class="num">' + dataset.n_points + '</td>' +
                        '<td class="kind">' + escapeHtml(dataset.kind_label) + '</td>' +
                        '<td>' + linksCell(dataset) + '</td>' +
                        '</tr>';
            });
        });
        html += '</table>';
        if (data.note) {
            html += '<div class="note">' + escapeHtml(data.note) + '</div>';
        }
        $('#summary').html(html);
        $('#xmlbox').show();
    }

    $('#generateXsams').click(function () {
        var query = 'select * ';
        var params = {};
        if ($(colltypes).val()) {
            query += "where CollisionIAEACode='" + $(colltypes).val() + "' ";
            params.collision_type = $(colltypes).val();
            if ($(species).val()) {
                query += "and InchiKey='" + $(species).val() + "' ";
                params.species = $(species).val();
            }
        }
        if ($(states).val()) params.state = $(states).val();
        if ($(cstypes).val()) params.cs_type = $(cstypes).val();

        var tap_url = base_url + '/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=' +
                      encodeURIComponent(query);
        $('#summary').html('<p>Searching...</p>');
        $.getJSON(base_url + '/search_results/', params)
            .done(renderSummary)
            .fail(function () { $('#summary').html('<p>Search failed.</p>'); });

        document.getElementById('XMLHolder').innerHTML = 'Loading...';
        LoadXML('XMLHolder', tap_url);
    });

});

(function ($) {
    $.fn.resetElem = function () {
        $(this).prop('disabled', true).html('<option value="" selected="selected">---------</option>');
    };
})(jQuery);
