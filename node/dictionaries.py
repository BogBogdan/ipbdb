from vamdctap.unitconv import *


# -*- coding: utf-8 -*-
"""
ExampleNode dictionary definitions.
"""

# The returnable dictionary is used internally by the node and defines
# all the ways the VAMDC standard keywords (left-hand side) maps to
# the internal database representation queryset (right-hand side)
#
# When writing this, it helps to remember that dictionary is applied
# in a loop to every matching *instance* of the queryset variables
# returned from queryfunc.py. So in the example below, all 'AtomStates'
# will be looped over by the node software, using the name 'AtomState'
# (singular). 'AtomState' will be one single instance of a matching
# database object, from which we extract everything we need by parsing
# the VAMDC_standard LHS of this dictionary to how it maps to our specific
# database on the RHS. So, when looping through all AtomState objects
# matching the given query, the generator will for example know that
# to get the AtomStateEnergy VAMDC value, it will need to look at
# the AtomState.energy, i.e. the "energy" property of the current
# database object being worked on.
#
# (if you look at queryfuncs.py, you'll see 'AtomStates' being
#  assigned)

RETURNABLES = {\
'NodeID' : 'IPBemol', # required
############################################################
'MethodID' : 'Method.id',
'MethodCategory' : 'Method.category',
############################################################

'MoleculeSpeciesId':'Molecule.id',
'MoleculeInchi':'Molecule.inchi',
'MoleculeInchiKey':'Molecule.inchikey',
'MoleculeChemicalName':'Molecule.name',
'MoleculeOrdinaryStructuralFormula':'Molecule.chemical_formula',
'MoleculeStoichiometricFormula':'Molecule.stoichiometric_formula',
'MoleculeMolecularWeight':'Molecule.molecular_weight',
'MoleculeIonCharge':'Molecule.ion_charge',
'AtomSpeciesId':'Atom.id',
'AtomInchi':'Atom.inchi',
'AtomInchiKey':'Atom.inchikey',
'AtomSymbol':'Atom.chemical_formula',

'AtomIonCharge':'Atom.ion_charge',
'AtomNuclearCharge':'Atom.nuclear_charge',

'AtomStateId':'AtomState.id',
'AtomStateConfigurationLabel':'AtomState.configuration',
'AtomStateDescription':'AtomState.description',
'AtomStateEnergy':'AtomState.treshold',
'AtomStateEnergyUnit':'AtomState.treshold_unit',

'MoleculeStateId':'MoleculeState.id',
'MoleculeStateDescription':'MoleculeState.term',
'MoleculeStateEnergy':'MoleculeState.treshold',
'MoleculeStateEnergyUnit':'MoleculeState.treshold_unit',

'ParticleName':'Particle.name',
'ParticleSpeciesID':'Particle.speciesid',
'ParticleCharge':'Particle.charge',
'ParticleComment':'Particle.comment',

#'AtomStateRef':'AtomState.Sources',
#'AtomStateEnergy':'AtomState.stateenergy',
#'AtomStateEnergyUnit':'AtomState.stateenergyunit.value',
#'AtomStateParity' : 'AtomState.parity.value',
#'AtomStateMixingCoeff':'Component.mixingcoefficient',
#'AtomStateMixingCoeffClass' : 'Component.mixingclass.value',
#'AtomStateLifeTime': 'AtomState.lifetime',
#'AtomStateStatisticalWeight' : 'AtomState.statisticalweight',
#'AtomStateStatisticalWeightUnit' : 'AtomState.statisticalweightunit.value',
#'AtomStateLifeTimeUnit': 'AtomState.lifetimeunit.value',
#'AtomStateLifeTimeDecay':'totalRadiative',
#'AtomStateIonizationEnergy' : 'AtomState.ionizationenergy',
#'AtomStateIonizationEnergyUnit' : 'AtomState.ionizationenergyunit.value',
#'AtomStateTotalAngMom' : 'AtomState.totalangularmomentum',
'AtomStateTermLabel' : 'AtomState.term',
'AtomStateTermLSL' : 'AtomState.term',
#'AtomStateConfigurationLabel' : 'Component.configuration',
#'AtomStateTermLSL' : 'Component.Lscoupling.l',
#'AtomStateTermLSS' : 'Component.Lscoupling.s',
#'AtomStateTermLSMultiplicity' : 'Component.Lscoupling.multiplicity',


'CollisionID':'CollTran.id',
'CollisionReactantState':'Reactant.stateref',
'CollisionReactantSpecies':'Reactant.speciesref',
'CollisionProductState':'Product.stateref',
'CollisionProductSpecies':'Product.speciesref',
'CollisionRef':'CollTran.sourcerefs',
'CollisionCode':'CollTran.collision_type.vamdc_code',
'CollisionIAEACode':'CollTran.collision_type.iaea_code',
'CollisionUserDefinition':'CollTran.collision_type.name',

'CollisionDataSetDescription':'DataSet.description',
#'CollisionDataSetRef':'DataSet.sourcerefs',

'SourceID':'Source.source_id',
'SourceCategory':'Source.category',
'SourceArticleNumber':'Source.article_number',
'SourceDOI':'Source.digital_object_id',
'SourcePageBegin':'Source.page_begin',
'SourcePageEnd':'Source.page_end',
'SourceTitle':'Source.title',
'SourceAuthorName':'Source.authnames',
'SourceURI':'Source.uri',
'SourceVolume':'Source.volume',
'SourceYear':'Source.year',
'SourceComments':'Source.comments',
}

# The restrictable dictionary defines limitations to the search.
# The left-hand side is standardized, the righ-hand size should
# be defined in Django query-language style, where e.g. a search
# for the Species.atomic field  would be written as species__atomic.

RESTRICTABLES = {\
#general
'CollisionIAEACode' : 'collision_type__iaea_code',
'CollisionCode' : 'collision_type__vamdc_code',
#'SourceDOI' : 'dataset_set__sources__digital_object_id',
#'SourceYear' : 'source__year',
#'SourceCategory' : 'source__category',

#general
'AtomSymbol' : 'product__species__chemical_formula',
'MoleculeChemicalName' : 'product__species__chemical_formula',
'MoleculeStoichiometricFormula' : 'product__species__stoichiometric_formula',
'MoleculeOrdinaryStructuralFormula' : 'product__species__chemical_formula',
'InchiKey' : 'product__species__inchikey',
'Inchi' : 'product__species__inchi',
'ParticleName' : test_constant(['electron']),

#only search for reactants
'reactant0.AtomSymbol' : 'reactant__species__chemical_formula',
'reactant0.MoleculeChemicalName' : 'reactant__species__name',
'reactant0.MoleculeStoichiometricFormula' : 'reactant__species__stoichiometric_formula',
'reactant0.MoleculeOrdinaryStructuralFormula' : 'reactant__species__chemical_formula',
'reactant0.InchiKey' : 'reactant__species__inchikey',
'reactant0.Inchi' : 'reactant__species__inchi',
'reactant0.ParticleName' : test_constant(['electron']),

#only search for reactants
'reactant1.AtomSymbol' : 'reactant__species__chemical_formula',
'reactant1.MoleculeChemicalName' : 'reactant__species__name',
'reactant1.MoleculeStoichiometricFormula' : 'reactant__species__stoichiometric_formula',
'reactant1.MoleculeOrdinaryStructuralFormula' : 'reactant__species__chemical_formula',
'reactant1.InchiKey' : 'reactant__species__inchikey',
'reactant1.Inchi' : 'reactant__species__inchi',
'reactant1.ParticleName' : test_constant(['electron']),

# collider is always an electron:

'collider.ParticleName':test_constant(['electron']),

# target could also be an origin_species
'target.AtomSymbol' : 'reactant__species__chemical_formula',
'target.MoleculeChemicalName' : 'reactant__species__name',
'target.MoleculeStoichiometricFormula' : 'reactant__species__stoichiometric_formula',
'target.MoleculeOrdinaryStructuralFormula' : 'reactant__species__chemical_formula',
'target.InchiKey' : 'reactant__species__inchikey',
'target.Inchi' : 'reactant__species__inchi',
'target.ParticleName' : test_constant(['electron']),


# only search for products
'product0.AtomSymbol' : 'product__species__chemical_formula',
'product0.MoleculeChemicalName' : 'product__species__name',
'product0.MoleculeStoichiometricFormula' : 'product__species__stoichiometric_formula',
'product0.MoleculeOrdinaryStructuralFormula' : 'product__species__chemical_formula',
'product0.InchiKey' : 'product__species__inchikey',
'product0.Inchi' : 'product__species__inchi',

}


