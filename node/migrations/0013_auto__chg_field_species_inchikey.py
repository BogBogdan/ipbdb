# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Species.inchikey'
        db.alter_column(u'species', 'inchikey', self.gf('django.db.models.fields.CharField')(max_length=128))

    def backwards(self, orm):

        # Changing field 'Species.inchikey'
        db.alter_column(u'species', 'inchikey', self.gf('django.db.models.fields.CharField')(max_length=20))

    models = {
        'node.author': {
            'Meta': {'ordering': "['name']", 'object_name': 'Author', 'db_table': "u'authors'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'node.collision': {
            'Meta': {'object_name': 'Collision', 'db_table': "u'collisions'"},
            'collision_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.CollisionType']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product'", 'to': "orm['node.SpeciesState']"}),
            'reactant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reactant'", 'to': "orm['node.SpeciesState']"})
        },
        'node.collisiontype': {
            'Meta': {'object_name': 'CollisionType', 'db_table': "u'collisiontypes'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'iaea_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'unique': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vamdc_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'node.crosssectiontype': {
            'Meta': {'object_name': 'CrossSectionType', 'db_table': "u'crosssectiontypes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'node.datalist': {
            'Meta': {'object_name': 'DataList', 'db_table': "u'datalists'"},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data_values': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'node.dataset': {
            'Meta': {'object_name': 'DataSet', 'db_table': "u'datasets'"},
            'collision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.Collision']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'data_sets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.Source']"})
        },
        'node.source': {
            'Meta': {'object_name': 'Source', 'db_table': "u'sources'"},
            'article_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sources'", 'symmetrical': 'False', 'to': "orm['node.Author']"}),
            'bibtex': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'digital_object_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_begin': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'page_end': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'source_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'node.species': {
            'Meta': {'object_name': 'Species', 'db_table': "u'species'"},
            'cas': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'chemical_formula': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inchi': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'inchikey': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'nuclear_charge': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'species_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.SpeciesType']"})
        },
        'node.speciesstate': {
            'Meta': {'object_name': 'SpeciesState', 'db_table': "u'speciesstates'"},
            'configuration': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'j': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.Species']"}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'treshold': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'treshold_unit': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'node.speciestype': {
            'Meta': {'object_name': 'SpeciesType', 'db_table': "u'speciestypes'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'node.tabulateddata': {
            'Meta': {'object_name': 'TabulatedData', 'db_table': "u'tabulateddata'"},
            'accuracy': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tabulated_data_accuracy'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.DataList']"}),
            'cross_section_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.CrossSectionType']"}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.DataSet']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'x': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tabulated_data_x'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.DataList']"}),
            'y': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tabulated_data_y'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.DataList']"})
        }
    }

    complete_apps = ['node']