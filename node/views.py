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

