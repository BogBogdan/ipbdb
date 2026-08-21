# -*- coding: utf-8 -*-
#
# This module (which must have the name queryfunc.py) is responsible
# for converting incoming queries to a database query understood by
# this particular node's database schema.
#
# This module must contain a function setupResults, taking a sql object
# as its only argument.
#

# library imports

import logging
from itertools import chain

from vamdctap.sqlparse import sql2Q
from .dictionaries import *

from . import models
import datetime

log = logging.getLogger("vamdc.node.queryfu")

LIMIT = 1000

class ReaProd:
    def __init__(self, stateid, speciesid):
        self.stateref = stateid
        self.speciesref = speciesid

class Particle:
    def __init__(self, type):
        if type == 'electron':
            self.charge = -1
            self.name = 'electron'
            self.speciesid = 'XElectron'
            self.comment = 'low energy electrons'

#------------------------------------------------------------
# Main function
#------------------------------------------------------------

def setupResults(sql):
    """
    This function is always called by the NodeSoftware.
    """
    # log the incoming query
    log.debug(sql)

    # convert the incoming sql to a correct django query syntax object
    # (sql2Q is a helper function to do this for us).
    q = sql2Q(sql)

    print(q)

    collisions = models.Collision.objects.filter(q)

    reactantids = set(collisions.values_list('reactant', flat=True))
    productids  = set(collisions.values_list('product',  flat=True))
    stateids = reactantids.union(productids)   
    states = models.SpeciesState.objects.filter(pk__in=stateids)
    atoms = []
    molecules = []
    particles = []
    sourceids = []

    lastmodifiedheader = datetime.datetime(1970, 1, 1, 1, 1)

    for state in states:
        if state.species.species_type.name == "Atom": atoms.append(state.species)
        elif state.species.species_type.name == "Molecule" : molecules.append(state.species)
    atoms = set(atoms)
    molecules = set(molecules)
    for atom in atoms:
	    atom.States = atom.speciesstate_set.filter(pk__in=stateids)
    for molecule in molecules:
        molecule.States = molecule.speciesstate_set.filter(pk__in=stateids)
    
    particles.append(Particle('electron'))

    nstates = len(states)
    nspecies  = len(atoms) + len(molecules)

    for coll in collisions:

        if coll.lastmodified > lastmodifiedheader:
            lastmodifiedheader = coll.lastmodified
        coll.Reactants = []
        coll.Products = []
        coll.sourcerefs = []
        coll.Reactants.append(ReaProd(coll.reactant.id, coll.reactant.species.id))
        coll.Reactants.append(ReaProd('', 'XElectron'))
        coll.Products.append(ReaProd(coll.product.id, coll.product.species.id))
        coll.DataSets  = models.DataSet.objects.filter(collision_id=coll.id)

        for dataset in coll.DataSets:
            for sourceid in dataset.sources.values_list('source_id', flat=True):
                sourceids.append(sourceid)
                coll.sourcerefs.append(sourceid)
            dataset.TabData = models.TabulatedData.objects.filter(dataset_id=dataset.id)
        #for dataset in coll.DataSets:
        #    dataset.sourcerefs = []
        #    for sourceid in dataset.sources.values_list('source_id', flat=True):
        #        sourceids.append(sourceid)
        #        coll.sourcerefs.append(sourceid)
        #
        #    dataset.TabData = models.TabulatedData.objects.filter(dataset_id=dataset.id)
    sources = models.Source.objects.filter(source_id__in=sourceids)
    for src in sources:
        src.authnames=src.authors.values_list('name', flat=True)

    nsources = len(sources)
    ncoll = len(collisions)
    natoms = len(atoms)
    nmolecules = len(molecules)
    ntrans = 0

    #make sure that lastmodifiedheader is not newer than now
    if lastmodifiedheader > datetime.datetime.now():
        lastmodifiedheader = datetime.datetime.now()

    # standardized and shouldn't be changed.
    headerinfo = {'COUNT-SOURCES'    : nsources,
                  'COUNT-SPECIES'    : nspecies,
                  'COUNT-ATOMS'      : natoms,
                  'COUNT-MOLECULES'  : nmolecules,
                  'COUNT-STATES'     : nstates,
		          'COUNT-COLLISIONS' : ncoll,
                  'COUNT-RADIATIVE'  : ntrans,
                  'LAST-MODIFIED'    : lastmodifiedheader,
                  }

    # Return the data. The keynames are standardized.
    if ncoll > 0:
        return {'Sources'    : sources,
    	        'CollTrans'  : collisions,
	            'Atoms'      : atoms,
                'Molecules'  : molecules,
	            'Particles'  : particles,
	            'HeaderInfo' : headerinfo,
                }
    else:
        return {}

