# Tests

Checks a running node over http. Nothing is written, the node is only read, so it is
safe to point at the review server as well as at a local checkout.

```
python run.py                        # the dev server, http://127.0.0.1:8001
python run.py http://165.227.150.114 # the review server
```

Any Python 3 works, only the standard library is used. One run is about 700 requests
and takes a minute and a half.

## test_pages

The search page answers, still carries the four dropdowns, and loads our
`beamdb-search.js` and not the production `combo-ajax.js`, which has
`servo.aob.rs` hard coded and would send a local page to query production.

`/plots/` must be gone, a graph is reached from the results table and not from a
listing of its own. Plotly and both of our scripts are served from this node, so
the pages do not depend on a cdn. The two
TAP service documents answer and parse, and `availability` says the node is up.
An unknown data set gives 404 rather than a server error.

## test_plots

Walks every data set the search page lists, with no filter set, and asks for all
three of its addresses.

The page renders and has a non empty title. `data.json` answers and reports a plot
type we know. The numbers behind the graph are then checked against themselves:
each energy carries as many cross section values as angles and as many errors, the
angles are in order, the point and energy and angle counts in the header match what
the series actually hold, a surface has one row per energy and each row is as wide
as the angle axis, and no value is missing or infinite. Finally the csv is parsed
and must have the right columns and exactly one row per drawn point.

A set whose axis lengths disagree cannot be drawn. Those must carry no series at
all and must say why, which is what the red warning on the site shows. The run
prints each flagged set so a change in the data is visible in the output.

## test_search

The summary table under the search form must report counts that match its own rows,
and every row must name its process, its cross section and its sources. The collision type filter must narrow the table and return only that type,
an unknown filter must return nothing.

The note about the XSAMS output must stay away when the filters can be passed on to
TAP and appear when they cannot. It must not read as a data problem, since red is
reserved for those.

## test_tap

Asks TAP for the whole node, parses the XSAMS, and counts blocks, sources and
species.

Then the part that matters: every measured point in the XSAMS is compared with
every point drawn on the site. Both sides are reduced to a sorted list of
energy, angle and cross section triples, so the comparison does not depend on the
order of the document or on how the lists are grouped into curves. Each XSAMS
block must find its graph and each graph must find its block. The blocks whose
axes disagree must be exactly the sets the site cannot draw.

The two paths share only the database. The table and the graphs come from
`node/plotting.py`, the XSAMS from `vamdctap`, so agreement means both read the
data the same way.

Last, every collision type the form offers is queried and the answer must be valid
XSAMS, and a query with no hits must give 204 rather than an error.
