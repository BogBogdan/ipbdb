import json
from django.template import RequestContext
from django.db.models import F
from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
#from django.template import Context
from django.http import HttpResponse
from node.models import *
from node.forms import Search_form
"""
def index(request):
    import dictionaries
    t = get_template('search.html')
    title = 'Search'
    req = ['All'];
    for a in dictionaries.REQUESTABLES:
        req.append(a);
    html = t.render (Context({'requestables':req}))
    return HttpResponse(html)
"""
def index(request):
    t = get_template('main.html')
    title = 'Search'
    f = Search_form()
    #html = t.render (Context({ 'f':f, }))
    html = t.render ({ 'f':f, })
    return HttpResponse(html)

def get_species(request, coll_type_id):
    collType = CollisionType.objects.get(iaea_code=coll_type_id)
    species = Species.objects.filter(speciesstate__product__collision_type=collType)
    species_dict = {}
    for spec in species:
        species_dict[spec.inchikey] = spec.name
    #return HttpResponse(json.dumps(species_dict), mimetype="application/json")
    return HttpResponse(json.dumps(species_dict))

def get_states(request, species_id, coll_type_id):
    species = Species.objects.get(inchikey=species_id)
    collType = CollisionType.objects.get(iaea_code=coll_type_id)    
    states = SpeciesState.objects.filter(product__collision_type=collType, species=species)
    states_dict = {}
    for state in states:
        states_dict[state.id] = state.term
    #return HttpResponse(json.dumps(states_dict), mimetype="application/json")
    return HttpResponse(json.dumps(states_dict))

def get_cs_types(request, state_id, coll_type_id):
    print(repr(request.GET))
    collType = CollisionType.objects.get(iaea_code=coll_type_id)
    state = SpeciesState.objects.get(pk=state_id)    
    cs_types = CrossSectionType.objects.filter(tabulateddata__dataset__collision__collision_type=collType, tabulateddata__dataset__collision__product=state)
    cs_dict = {}
    for cs_type in cs_types:
        cs_dict[cs_type.id] = cs_type.name
    #return HttpResponse(json.dumps(cs_dict), mimetype="application/json")
    return HttpResponse(json.dumps(cs_dict))

# --- plots, added on top of the original views ---
import csv
from urllib.parse import quote

from django.http import JsonResponse
from django.shortcuts import render

from node import plotting


def tabulated_data():
    return (TabulatedData.objects
            .select_related('cross_section_type',
                            'dataset__collision__collision_type',
                            'dataset__collision__reactant__species',
                            'dataset__collision__product')
            .prefetch_related('x', 'y', 'accuracy', 'dataset__sources')
            .order_by('id'))


def below_minimum(value, wanted):
    return wanted.isdigit() and value < int(wanted)


def plots_index(request):
    kind = request.GET.get('kind') or ''
    target = (request.GET.get('target') or '').strip()
    cs_type = (request.GET.get('cs') or '').strip()
    min_energies = (request.GET.get('min_energies') or '').strip()
    min_angles = (request.GET.get('min_angles') or '').strip()
    min_points = (request.GET.get('min_points') or '').strip()

    rows = []
    counts = {}
    cs_types = set()
    targets = set()
    for tabdata in tabulated_data():
        meta = plotting.prepare(tabdata)
        counts[meta['kind']] = counts.get(meta['kind'], 0) + 1
        cs_types.add(meta['cs_type'])
        name = meta['target_formula'] or meta['target']
        targets.add(name)
        if kind and meta['kind'] != kind:
            continue
        if target and target != name:
            continue
        if cs_type and meta['cs_type'] != cs_type:
            continue
        if below_minimum(meta['n_energies'], min_energies):
            continue
        if below_minimum(meta['n_angles'], min_angles):
            continue
        if below_minimum(meta['n_points'], min_points):
            continue
        rows.append({'id': meta['id'],
                     'title': plotting.title(meta),
                     'cs_type': meta['cs_type'],
                     'kind': meta['kind'],
                     'kind_label': plotting.KIND_LABELS[meta['kind']],
                     'n_energies': meta['n_energies'],
                     'n_angles': meta['n_angles'],
                     'n_points': meta['n_points'],
                     'problems': meta['problems']})

    summary = [{'kind': key, 'label': plotting.KIND_LABELS[key], 'n': counts[key]}
               for key in sorted(counts, key=lambda key: -counts[key])]
    return render(request, 'plots_index.html', {'rows': rows,
                                                'summary': summary,
                                                'total': sum(counts.values()),
                                                'targets': sorted(targets),
                                                'cs_types': sorted(cs_types),
                                                'energy_steps': [2, 3, 5, 10, 20],
                                                'angle_steps': [5, 10, 20, 50, 100],
                                                'point_steps': [50, 100, 250, 500, 1000],
                                                'kind_filter': kind,
                                                'target_filter': target,
                                                'cs_filter': cs_type,
                                                'min_energies': min_energies,
                                                'min_angles': min_angles,
                                                'min_points': min_points})


def plot_detail(request, td_id):
    tabdata = get_object_or_404(tabulated_data(), pk=td_id)
    meta = plotting.prepare(tabdata)
    return render(request, 'plot.html',
                  {'meta': meta,
                   'meta_json': json.dumps(meta),
                   'title': plotting.title(meta),
                   'kind_label': plotting.KIND_LABELS[meta['kind']]})


def plot_json(request, td_id):
    tabdata = get_object_or_404(tabulated_data(), pk=td_id)
    meta = plotting.prepare(tabdata)
    meta['title'] = plotting.title(meta)
    meta['kind_label'] = plotting.KIND_LABELS[meta['kind']]
    return JsonResponse(meta)


def plot_csv(request, td_id):
    tabdata = get_object_or_404(tabulated_data(), pk=td_id)
    meta = plotting.prepare(tabdata)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=ipbdb-%s.csv' % td_id
    writer = csv.writer(response)
    if meta['kind'] == 'curve_e':
        writer.writerow(['energy_%s' % meta['unit_energy'],
                         '%s_%s' % (meta['cs_type'], meta['unit_y']), 'error'])
        for series in meta['series']:
            for i in range(len(series['x'])):
                writer.writerow([series['x'][i], series['y'][i], series['error'][i]])
    else:
        writer.writerow(['energy_%s' % meta['unit_energy'],
                         'angle_%s' % meta['unit_angle'],
                         '%s_%s' % (meta['cs_type'], meta['unit_y']), 'error'])
        for series in meta['series']:
            for i in range(len(series['angle'])):
                writer.writerow([series['energy'], series['angle'][i],
                                 series['y'][i], series['error'][i]])
    return response


def search_results(request):
    coll_code = (request.GET.get('collision_type') or '').strip()
    inchikey = (request.GET.get('species') or '').strip()
    state_id = (request.GET.get('state') or '').strip()
    cs_id = (request.GET.get('cs_type') or '').strip()

    collisions = Collision.objects.all()
    terms = []
    if coll_code:
        collisions = collisions.filter(collision_type__iaea_code=coll_code)
        terms.append("CollisionIAEACode='%s'" % coll_code)
    if inchikey:
        collisions = collisions.filter(product__species__inchikey=inchikey)
        terms.append("InchiKey='%s'" % inchikey)
    if state_id.isdigit():
        collisions = collisions.filter(product_id=int(state_id))

    sets = tabulated_data().filter(dataset__collision__in=collisions)
    if cs_id.isdigit():
        sets = sets.filter(cross_section_type_id=int(cs_id))

    groups = {}
    order = []
    sources = set()
    total = 0
    for tabdata in sets:
        meta = plotting.prepare(tabdata)
        collision = tabdata.dataset.collision
        if collision.id not in groups:
            groups[collision.id] = {'collision_id': collision.id,
                                    'collision_type': meta['collision_type'],
                                    'target': meta['target'],
                                    'target_formula': meta['target_formula'],
                                    'product': meta['product'],
                                    'product_formula': meta['product_formula'],
                                    'product_state': meta['product_state'],
                                    'datasets': []}
            order.append(collision.id)
        groups[collision.id]['datasets'].append(
            {'id': meta['id'],
             'cs_type': meta['cs_type'],
             'cs_name': meta['cs_name'],
             'kind': meta['kind'],
             'kind_label': plotting.KIND_LABELS[meta['kind']],
             'n_points': meta['n_points'],
             'problems': meta['problems']})
        sources.update(meta['sources'])
        total += 1

    query = 'select * ' + ('where ' + ' and '.join(terms) if terms else '')
    tap_url = '/tap/sync?REQUEST=doQuery&LANG=VSS2&FORMAT=XSAMS&QUERY=' + quote(query)

    # vss2 has no keyword for cross section type or for a single state
    note = ''
    if cs_id.isdigit() or state_id.isdigit():
        note = ('The XSAMS document is wider than this table because the query '
                'language cannot filter on cross section type or on a single state.')

    result = {'query': query,
              'note': note,
              'tap_url': tap_url,
              'counts': {'collisions': len(order),
                         'datasets': total,
                         'sources': len(sources)},
              'groups': [groups[key] for key in order]}
    return JsonResponse(result)
