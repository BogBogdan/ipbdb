# The summary table on the search page and the filters above it.

from client import listed
from test_plots import data_set_ids


def checks(site):
    ids = data_set_ids(site)

    status, result = site.json('/search_results/')
    yield ('search without a filter answers', status == 200 and result is not None,
           'http %s' % status)
    if not result:
        return

    found = sorted(dataset['id'] for group in result['groups']
                   for dataset in group['datasets'])
    yield ('the table holds every data set', found == ids,
           '%d rows' % len(found))
    yield ('the counts agree with the rows',
           result['counts']['datasets'] == len(found)
           and result['counts']['collisions'] == len(result['groups']),
           '%s' % result['counts'])

    incomplete = []
    for group in result['groups']:
        if not group['collision_type'] or not (group['target_formula'] or group['target']):
            incomplete.append(group['collision_id'])
        for dataset in group['datasets']:
            if not dataset['kind_label'] or not dataset['cs_name']:
                incomplete.append(dataset['id'])
    yield ('every row names its process and cross section', not incomplete,
           listed(incomplete) or '%d rows' % len(found))

    sourced = sum(1 for group in result['groups']
                  for dataset in group['datasets'] if dataset['sources'])
    with_doi = sum(1 for group in result['groups'] for dataset in group['datasets']
                   for source in dataset['sources'] if source['doi'])
    yield ('rows carry their sources', sourced == len(found),
           '%d of %d rows, %d source links with a doi' % (sourced, len(found), with_doi))

    status, elastic = site.json('/search_results/?collision_type=EEL')
    ok = elastic is not None and 0 < len(elastic['groups']) < len(result['groups'])
    wrong = [group['collision_id'] for group in (elastic['groups'] if elastic else [])
             if group['collision_type'] != 'Elastic']
    yield ('the collision type filter narrows the table', ok and not wrong,
           '%d of %d collisions%s' % (len(elastic['groups']) if elastic else 0,
                                      len(result['groups']),
                                      ', wrong: ' + listed(wrong) if wrong else ''))

    status, nothing = site.json('/search_results/?collision_type=NOSUCH')
    yield ('an unknown filter returns nothing',
           nothing is not None and not nothing['groups'], 'http %s' % status)

    yield ('no note when the xml can follow the filters', result['note'] == '',
           repr(result['note'][:40]))
    status, narrowed = site.json('/search_results/?collision_type=EEL&cs_type=1')
    yield ('a note when the xml cannot follow the filters',
           narrowed is not None and bool(narrowed['note']),
           (narrowed['note'][:60] + '...') if narrowed and narrowed['note'] else 'missing')
    yield ('the note is advice, not a data problem',
           narrowed is not None and 'problem' not in narrowed['note'].lower(),
           'rendered grey, the red colour is kept for data problems')
