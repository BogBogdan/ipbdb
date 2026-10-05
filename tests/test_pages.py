# The plain pages, the static files and the two TAP service documents.

import xml.etree.ElementTree as ET

from client import listed

STATIC = ['/static/js/plotly.min.js',
          '/static/js/beamdb-plot.js',
          '/static/js/beamdb-search.js']


def checks(site):
    status, text = site.text('/')
    yield ('search page answers', status == 200, 'http %s' % status)
    yield ('search page carries the form',
           'generateXsams' in text and text.count('<select') == 4,
           '%d selects' % text.count('<select'))
    yield ('search page loads our script',
           'beamdb-search.js' in text and 'combo-ajax.js' not in text,
           'combo-ajax.js is the production one and queries servo.aob.rs')

    status, body = site.fetch('/plots/')
    yield ('there is no separate data set listing', status == 404,
           'http %s, plots are reached from the search page' % status)

    missing = []
    for path in STATIC:
        status, body = site.fetch(path)
        if status != 200 or not body:
            missing.append(path)
    yield ('static files are served', not missing, listed(missing) or '%d files' % len(STATIC))

    status, body = site.fetch('/static/js/plotly.min.js')
    yield ('plotly is served by us, not a cdn', len(body) > 1000000,
           '%.1f MB' % (len(body) / 1048576.0))

    status, text = site.text('/tap/availability')
    available = False
    if status == 200:
        try:
            available = 'true' in ET.fromstring(text.encode('utf-8')).find(
                '{http://www.ivoa.net/xml/VOSIAvailability/v1.0}available').text
        except Exception:
            available = False
    yield ('tap availability says the node is up', available, 'http %s' % status)

    status, text = site.text('/tap/capabilities')
    parsed = False
    if status == 200:
        try:
            ET.fromstring(text.encode('utf-8'))
            parsed = True
        except ET.ParseError as error:
            parsed = str(error)
    yield ('tap capabilities is valid xml', parsed is True,
           'http %s %s' % (status, '' if parsed is True else parsed))

    status, body = site.fetch('/admin/')
    yield ('admin asks for a login', status in (200, 302), 'http %s' % status)

    status, body = site.fetch('/plots/999999/')
    yield ('a missing data set gives 404', status == 404, 'http %s' % status)
