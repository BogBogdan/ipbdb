# The TAP service, and the XSAMS numbers against the numbers we draw.

import re
import xml.etree.ElementTree as ET

from client import listed
from test_plots import data_set_ids

NS = '{http://vamdc.org/xml/xsams/1.0}'
EVERYTHING = "/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=select%20*"


def numbers(text):
    # values come space, comma or tab separated, the same as in node/plotting.py
    for separator in (',', ';', '	'):
        text = (text or '').replace(separator, ' ')
    return text.split()


def axis_kind(parameter):
    # same reading as node/plotting.py, a loss axis counts as the energy axis
    name = (parameter or '').lower()
    if 'loss' in name:
        return 'energy'
    if 'angle' in name:
        return 'angle'
    return 'energy'


def key(point):
    energy, angle, value = point
    return (energy, -1.0 if angle is None else angle, value)


def xsams_points(block):
    """every measured point of one XSAMS block, or None if the axes disagree"""
    axes = {}
    for node in block.findall(NS + 'X'):
        values = numbers(node.find(NS + 'DataList').text)
        axes.setdefault(axis_kind(node.get('parameter')), values)
    y = block.find(NS + 'Y/' + NS + 'DataList')
    values = numbers(y.text) if y is not None else []
    energy = axes.get('energy', [])
    angle = axes.get('angle', [])
    if len(energy) != len(values) or (angle and len(angle) != len(values)):
        return None
    angles = [float(a) for a in angle] if angle else [None] * len(values)
    return tuple(sorted(((float(energy[i]), angles[i], float(values[i]))
                         for i in range(len(values))), key=key))


def plot_points(meta):
    """the same points as the graph draws them"""
    points = []
    for series in meta['series']:
        if meta['kind'] == 'curve_e':
            for i in range(len(series['x'])):
                points.append((float(series['x'][i]), None, float(series['y'][i])))
        else:
            for i in range(len(series['angle'])):
                points.append((float(series['energy']), float(series['angle'][i]),
                               float(series['y'][i])))
    return tuple(sorted(points, key=key))


def checks(site):
    ids = data_set_ids(site)

    status, text = site.text(EVERYTHING, timeout=600)
    yield ('tap returns the whole node', status == 200, 'http %s, %d bytes'
           % (status, len(text)))
    if status != 200:
        return
    try:
        root = ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as error:
        yield ('the xsams document is valid xml', False, str(error))
        return
    yield ('the xsams document is valid xml', True, '%d bytes' % len(text))

    blocks = list(root.iter(NS + 'TabulatedData'))
    yield ('xsams carries every data set', len(blocks) == len(ids),
           '%d blocks, %d sets on the site' % (len(blocks), len(ids)))

    sources = len(list(root.iter(NS + 'Source'))) - 1    # one is the query itself
    yield ('xsams carries the sources', sources > 0, '%d sources' % sources)
    yield ('xsams carries the species',
           len(list(root.iter(NS + 'Atom'))) + len(list(root.iter(NS + 'Molecule'))) > 0,
           '%d atoms, %d molecules' % (len(list(root.iter(NS + 'Atom'))),
                                       len(list(root.iter(NS + 'Molecule')))))

    # every block must appear, point for point, in some graph on the site
    drawn = {}
    undrawable = []
    for td_id in ids:
        status, meta = site.json('/plots/%d/data.json' % td_id)
        if meta is None:
            continue
        if meta['kind'] == 'invalid':
            undrawable.append(td_id)
            continue
        drawn.setdefault(plot_points(meta), []).append(td_id)

    unreadable, missing = [], []
    for position, block in enumerate(blocks):
        points = xsams_points(block)
        if points is None:
            unreadable.append(position)
            continue
        if points in drawn and drawn[points]:
            drawn[points].pop()
        else:
            missing.append(position)

    yield ('xsams blocks with disagreeing axes are the ones we cannot draw',
           len(unreadable) == len(undrawable),
           '%d in xsams, %d on the site (%s)'
           % (len(unreadable), len(undrawable), listed(undrawable)))
    yield ('every xsams measurement is drawn on the site', not missing,
           listed(missing) or '%d blocks compared' % (len(blocks) - len(unreadable)))
    left = [td_id for group in drawn.values() for td_id in group]
    yield ('every graph on the site is in xsams', not left, listed(left) or 'none left over')

    status, text = site.text('/')
    codes = re.findall(r'<option value="([A-Z]{3})"', text)
    yield ('the form offers collision types', bool(codes), ', '.join(codes))

    bad = []
    for code in codes:
        query = "/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=" \
                "select%%20*%%20where%%20CollisionIAEACode='%s'" % code
        status, body = site.text(query, timeout=600)
        if status == 204:
            continue
        if status != 200:
            bad.append('%s http %s' % (code, status))
            continue
        try:
            ET.fromstring(body.encode('utf-8'))
        except ET.ParseError as error:
            bad.append('%s %s' % (code, error))
    yield ('every collision type gives valid xsams', not bad,
           listed(bad, 4) or '%d queries' % len(codes))

    status, body = site.text("/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS"
                             "&QUERY=select%20*%20where%20CollisionIAEACode='NOPE'")
    yield ('a query with no hits gives 204, not an error', status == 204, 'http %s' % status)
