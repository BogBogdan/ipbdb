# Every data set, one by one: the page, the numbers behind the graph, and the csv.

import csv
import io
import math
import re

from client import listed

KINDS = ['surface', 'waterfall', 'curve_theta', 'curve_e', 'invalid']


def data_set_ids(site):
    # the search page with no filter lists every set
    status, result = site.json('/search_results/')
    if not result:
        return []
    return sorted(dataset['id'] for group in result['groups']
                  for dataset in group['datasets'])


def finite(values):
    return all(value is None or (isinstance(value, float) and math.isfinite(value))
               or isinstance(value, int) for value in values)


def series_faults(meta):
    # everything the drawing code relies on, checked against the set itself
    faults = []
    kind = meta['kind']

    if kind == 'invalid':
        if meta['series']:
            faults.append('invalid but carries series')
        if not meta['problems']:
            faults.append('invalid without a reason')
        return faults

    if not meta['series']:
        faults.append('no series to draw')
        return faults

    points = 0
    energies, angles = set(), set()
    for series in meta['series']:
        if kind == 'curve_e':
            axis = series['x']
            if series['energy'] is not None:
                faults.append('curve_e series pinned to one energy')
        else:
            axis = series['angle']
            if series['energy'] is None:
                faults.append('series without an energy')
            else:
                energies.add(series['energy'])
            angles.update(axis)
            if axis != sorted(axis):
                faults.append('angles are not in order')
        if not (len(axis) == len(series['y']) == len(series['error'])):
            faults.append('axis %d, y %d, error %d'
                          % (len(axis), len(series['y']), len(series['error'])))
        if not finite(axis) or not finite(series['y']):
            faults.append('a value is not a finite number')
        points += len(axis)

    if kind == 'curve_e':
        energies = set(meta['series'][0]['x'])
    if points != meta['n_points']:
        faults.append('n_points says %d, series hold %d' % (meta['n_points'], points))
    if len(energies) != meta['n_energies']:
        faults.append('n_energies says %d, series hold %d'
                      % (meta['n_energies'], len(energies)))
    if len(angles) != meta['n_angles']:
        faults.append('n_angles says %d, series hold %d'
                      % (meta['n_angles'], len(angles)))

    if kind == 'curve_theta' and len(meta['series']) != 1:
        faults.append('curve_theta with %d energies' % len(meta['series']))
    if kind in ('surface', 'waterfall') and len(meta['series']) < 2:
        faults.append('%s with one energy' % kind)
    if kind == 'surface':
        if len(meta.get('z', [])) != len(meta.get('energies', [])):
            faults.append('the surface grid does not match the energies')
        if any(len(row) != len(meta.get('angles', [])) for row in meta.get('z', [])):
            faults.append('a surface row is not as wide as the angle axis')
    return faults


def checks(site):
    ids = data_set_ids(site)
    yield ('the search page lists data sets', bool(ids), '%d sets' % len(ids))
    if not ids:
        return

    bad_page, bad_json, bad_kind, bad_series, bad_csv, bad_title = [], [], [], [], [], []
    kinds = dict((kind, 0) for kind in KINDS)
    flagged = []

    for td_id in ids:
        status, text = site.text('/plots/%d/' % td_id)
        if status != 200 or 'id="plotdata"' not in text or 'beamdb-plot.js' not in text:
            bad_page.append(td_id)
        title = re.search(r'<div class="title">([^<]*)</div>', text)
        if not title or not title.group(1).strip():
            bad_title.append(td_id)

        status, meta = site.json('/plots/%d/data.json' % td_id)
        if status != 200 or meta is None:
            bad_json.append(td_id)
            continue
        if meta['kind'] not in KINDS or meta['id'] != td_id:
            bad_kind.append(td_id)
            continue
        kinds[meta['kind']] += 1
        if meta['problems']:
            flagged.append((td_id, '; '.join(meta['problems'])))

        faults = series_faults(meta)
        if faults:
            bad_series.append('#%d %s' % (td_id, faults[0]))

        status, body = site.text('/plots/%d/data.csv' % td_id)
        if status != 200:
            bad_csv.append('#%d http %s' % (td_id, status))
        else:
            rows = list(csv.reader(io.StringIO(body)))
            header = rows[0] if rows else []
            wanted = 3 if meta['kind'] == 'curve_e' else 4
            drawn = 0 if meta['kind'] == 'invalid' else meta['n_points']
            if len(header) != wanted or len(rows) - 1 != drawn:
                bad_csv.append('#%d %d columns, %d rows, expected %d and %d'
                               % (td_id, len(header), len(rows) - 1, wanted, drawn))

    yield ('every plot page renders', not bad_page, listed(bad_page) or '%d pages' % len(ids))
    yield ('every plot page has a title', not bad_title, listed(bad_title) or 'all named')
    yield ('every data.json answers', not bad_json, listed(bad_json) or '%d files' % len(ids))
    yield ('every set has a known plot type', not bad_kind, listed(bad_kind) or
           ', '.join('%s %d' % (kind, kinds[kind]) for kind in KINDS if kinds[kind]))
    yield ('the numbers behind every graph hold together', not bad_series,
           listed(bad_series, 4) or '%d sets' % len(ids))
    yield ('every csv matches its graph', not bad_csv,
           listed(bad_csv, 4) or '%d files' % len(ids))

    drawable = len(ids) - kinds['invalid']
    yield ('every set either draws or says why not',
           drawable + kinds['invalid'] == len(ids),
           '%d draw a graph, %d cannot and are marked' % (drawable, kinds['invalid']))
    for td_id, problem in flagged:
        yield ('  set #%d is flagged' % td_id, True, problem)
