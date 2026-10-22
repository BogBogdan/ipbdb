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

import csv
import datetime

from django.http import JsonResponse
from django.shortcuts import render

from vamdctap.generators import Xsams

from node import plotting
from node import queryfunc
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


def tabulated_data():
    return (TabulatedData.objects
            .select_related('cross_section_type',
                            'dataset__collision__collision_type',
                            'dataset__collision__reactant__species',
                            'dataset__collision__product')
            .prefetch_related('x', 'y', 'accuracy', 'dataset__sources')
            .order_by('id'))


def one_set(td_id):
    return plotting.prepare(get_object_or_404(tabulated_data(), pk=td_id))


def plot_detail(request, td_id):
    meta = one_set(td_id)
    return render(request, 'plot.html',
                  {'meta': meta,
                   'meta_json': json.dumps(meta),
                   'title': plotting.title(meta),
                   'kind_label': plotting.KIND_LABELS[meta['kind']]})


def plot_json(request, td_id):
    meta = one_set(td_id)
    meta['title'] = plotting.title(meta)
    meta['kind_label'] = plotting.KIND_LABELS[meta['kind']]
    return JsonResponse(meta)


def file_name(meta, suffix):
    # the description names the set, a file name cannot carry every character
    name = '-'.join(''.join(c if c.isalnum() else ' ' for c in meta['description']).split())
    stem = 'ipbdb-%s-%s' % (meta['id'], name) if name else 'ipbdb-%s' % meta['id']
    return '%s.%s' % (stem, suffix)


def plot_csv(request, td_id):
    meta = one_set(td_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name(meta, 'csv')
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


class OneSetQuery:
    # the generator reads these off the tap query, and one set is not a query
    requestables = []
    token = ''

    def __init__(self, request, meta):
        self.fullurl = request.build_absolute_uri()
        self.query = 'tabulated data %s, %s' % (meta['id'], meta['description'])


def xsams_data(tabdata):
    # what queryfunc hands the generator for a search, holding this set alone
    collision = tabdata.dataset.collision
    states = {state.id: state for state in (collision.reactant, collision.product)}
    atoms = []
    molecules = []
    species = {state.species_id: state.species for state in states.values()}
    for one in species.values():
        one.States = [state for state in states.values() if state.species_id == one.id]
        if one.species_type.name == 'Atom':
            atoms.append(one)
        else:
            molecules.append(one)

    sources = list(tabdata.dataset.sources.all())
    for source in sources:
        source.authnames = source.authors.values_list('name', flat=True)

    collision.Reactants = [queryfunc.ReaProd(collision.reactant_id, collision.reactant.species_id),
                           queryfunc.ReaProd('', 'XElectron')]
    collision.Products = [queryfunc.ReaProd(collision.product_id, collision.product.species_id)]
    collision.sourcerefs = [source.source_id for source in sources]
    collision.DataSets = [tabdata.dataset]
    tabdata.dataset.TabData = [tabdata]

    return {'Sources': sources,
            'CollTrans': [collision],
            'Atoms': atoms,
            'Molecules': molecules,
            'Particles': [queryfunc.Particle('electron')],
            'HeaderInfo': {'COUNT-SOURCES': len(sources),
                           'COUNT-SPECIES': len(species),
                           'COUNT-ATOMS': len(atoms),
                           'COUNT-MOLECULES': len(molecules),
                           'COUNT-STATES': len(states),
                           'COUNT-COLLISIONS': 1,
                           'COUNT-RADIATIVE': 0,
                           'LAST-MODIFIED': min(collision.lastmodified,
                                                datetime.datetime.now())}}


def indented(document):
    # the generator writes a whole section on one line, which no editor can fold
    lines = []
    depth = 0
    for line in document.replace('><', '>\n<').split('\n'):
        opens = (line.startswith('<') and not line.startswith('</')
                 and not line.startswith('<?') and not line.endswith('/>')
                 and '</' not in line)
        if line.startswith('</'):
            depth -= 1
        lines.append('  ' * max(depth, 0) + line)
        if opens:
            depth += 1
    return '\n'.join(lines)


def plot_xsams(request, td_id):
    tabdata = get_object_or_404(tabulated_data(), pk=td_id)
    meta = plotting.prepare(tabdata)
    document = ''.join(Xsams(tap=OneSetQuery(request, meta), **xsams_data(tabdata)))
    response = HttpResponse(indented(document), content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name(meta, 'xsams')
    return response


def search_results(request):
    coll_code = (request.GET.get('collision_type') or '').strip()
    inchikey = (request.GET.get('species') or '').strip()
    state_id = (request.GET.get('state') or '').strip()
    cs_id = (request.GET.get('cs_type') or '').strip()

    collisions = Collision.objects.all()
    if coll_code:
        collisions = collisions.filter(collision_type__iaea_code=coll_code)
    if inchikey:
        collisions = collisions.filter(product__species__inchikey=inchikey)
    if state_id.isdigit():
        collisions = collisions.filter(product_id=int(state_id))

    sets = tabulated_data().filter(dataset__collision__in=collisions)
    if cs_id.isdigit():
        sets = sets.filter(cross_section_type_id=int(cs_id))

    groups = {}
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
        groups[collision.id]['datasets'].append(
            {'id': meta['id'],
             'cs_type': meta['cs_type'],
             'cs_name': meta['cs_name'],
             'kind': meta['kind'],
             'kind_label': plotting.KIND_LABELS[meta['kind']],
             'n_points': meta['n_points'],
             'sources': meta['sources'],
             'problems': meta['problems']})
        sources.update(source['id'] for source in meta['sources'])
        total += 1

    # vss2 has no keyword for cross section type or for a single state
    note = ''
    if cs_id.isdigit() or state_id.isdigit():
        note = ('The XSAMS output below also holds the other cross section types '
                'and states of these collisions, the TAP query language cannot '
                'narrow it down to the selection above.')

    result = {'note': note,
              'counts': {'collisions': len(groups),
                         'datasets': total,
                         'sources': len(sources)},
              'groups': list(groups.values())}
    return JsonResponse(result)
