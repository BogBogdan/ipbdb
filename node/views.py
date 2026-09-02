import csv
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template

from urllib.parse import quote

from node import plotting
from node.models import *
from node.forms import Search_form


def index(request):
    template = get_template('main.html')
    return HttpResponse(template.render({'f': Search_form()}))


def get_species(request, coll_type_id):
    coll_type = get_object_or_404(CollisionType, iaea_code=coll_type_id)
    species = Species.objects.filter(
        speciesstate__product__collision_type=coll_type).distinct()
    result = {}
    for item in species:
        result[item.inchikey] = item.name
    return HttpResponse(json.dumps(result), content_type='application/json')


def get_states(request, species_id, coll_type_id):
    coll_type = get_object_or_404(CollisionType, iaea_code=coll_type_id)
    species = get_object_or_404(Species, inchikey=species_id)
    states = SpeciesState.objects.filter(
        species=species, product__collision_type=coll_type).distinct()
    result = {}
    for state in states:
        result[state.id] = plotting.state_label(state) or str(state.id)
    return HttpResponse(json.dumps(result), content_type='application/json')


def get_cs_types(request, state_id, coll_type_id):
    coll_type = get_object_or_404(CollisionType, iaea_code=coll_type_id)
    state = get_object_or_404(SpeciesState, pk=state_id)
    cs_types = CrossSectionType.objects.filter(
        tabulateddata__dataset__collision__collision_type=coll_type,
        tabulateddata__dataset__collision__product=state).distinct()
    result = {}
    for cs_type in cs_types:
        result[cs_type.id] = cs_type.name
    return HttpResponse(json.dumps(result), content_type='application/json')


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
    for tabdata in tabulated_data():
        meta = plotting.prepare(tabdata)
        counts[meta['kind']] = counts.get(meta['kind'], 0) + 1
        cs_types.add(meta['cs_type'])
        name = meta['target_formula'] or meta['target']
        if kind and meta['kind'] != kind:
            continue
        if target and target.lower() not in name.lower():
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
                                                'cs_types': sorted(cs_types),
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
