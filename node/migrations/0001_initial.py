# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SpeciesType'
        db.create_table(u'speciestypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('node', ['SpeciesType'])

        # Adding model 'Species'
        db.create_table(u'species', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('inchi', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('inchikey', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('chemical_formula', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('cas', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('species_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.SpeciesType'])),
        ))
        db.send_create_signal('node', ['Species'])

        # Adding model 'SpeciesState'
        db.create_table(u'speciesstates', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('configuration', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('treshold', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('j', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.Species'])),
        ))
        db.send_create_signal('node', ['SpeciesState'])

        # Adding model 'CollisionType'
        db.create_table(u'collisiontypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('iaea_code', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('vamdc_code', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['CollisionType'])

        # Adding model 'Collision'
        db.create_table(u'collisions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reactant', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reactant', to=orm['node.SpeciesState'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='product', to=orm['node.SpeciesState'])),
            ('collision_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.CollisionType'])),
        ))
        db.send_create_signal('node', ['Collision'])

        # Adding model 'CrossSectionType'
        db.create_table(u'crosssectiontypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['CrossSectionType'])

        # Adding model 'Author'
        db.create_table(u'authors', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('institution', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['Author'])

        # Adding model 'Source'
        db.create_table(u'sources', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('article_number', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('digital_object_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('source_id', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('page_begin', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('page_end', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('volume', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('source_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('bibtex', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('comments', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['Source'])

        # Adding M2M table for field authors on 'Source'
        db.create_table(u'sources_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['node.source'], null=False)),
            ('author', models.ForeignKey(orm['node.author'], null=False))
        ))
        db.create_unique(u'sources_authors', ['source_id', 'author_id'])

        # Adding model 'DataSet'
        db.create_table(u'datasets', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.Collision'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['DataSet'])

        # Adding M2M table for field sources on 'DataSet'
        db.create_table(u'datasets_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataset', models.ForeignKey(orm['node.dataset'], null=False)),
            ('source', models.ForeignKey(orm['node.source'], null=False))
        ))
        db.create_unique(u'datasets_sources', ['dataset_id', 'source_id'])

        # Adding model 'DataList'
        db.create_table(u'datalists', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('data_values', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('node', ['DataList'])

        # Adding model 'TabulatedData'
        db.create_table(u'tabulateddata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.DataSet'], null=True, blank=True)),
            ('cross_section_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['node.CrossSectionType'])),
        ))
        db.send_create_signal('node', ['TabulatedData'])

        # Adding M2M table for field y on 'TabulatedData'
        db.create_table(u'tabulateddata_y', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tabulateddata', models.ForeignKey(orm['node.tabulateddata'], null=False)),
            ('datalist', models.ForeignKey(orm['node.datalist'], null=False))
        ))
        db.create_unique(u'tabulateddata_y', ['tabulateddata_id', 'datalist_id'])

        # Adding M2M table for field x on 'TabulatedData'
        db.create_table(u'tabulateddata_x', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tabulateddata', models.ForeignKey(orm['node.tabulateddata'], null=False)),
            ('datalist', models.ForeignKey(orm['node.datalist'], null=False))
        ))
        db.create_unique(u'tabulateddata_x', ['tabulateddata_id', 'datalist_id'])

        # Adding M2M table for field accuracy on 'TabulatedData'
        db.create_table(u'tabulateddata_accuracy', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tabulateddata', models.ForeignKey(orm['node.tabulateddata'], null=False)),
            ('datalist', models.ForeignKey(orm['node.datalist'], null=False))
        ))
        db.create_unique(u'tabulateddata_accuracy', ['tabulateddata_id', 'datalist_id'])


    def backwards(self, orm):
        
        # Deleting model 'SpeciesType'
        db.delete_table(u'speciestypes')

        # Deleting model 'Species'
        db.delete_table(u'species')

        # Deleting model 'SpeciesState'
        db.delete_table(u'speciesstates')

        # Deleting model 'CollisionType'
        db.delete_table(u'collisiontypes')

        # Deleting model 'Collision'
        db.delete_table(u'collisions')

        # Deleting model 'CrossSectionType'
        db.delete_table(u'crosssectiontypes')

        # Deleting model 'Author'
        db.delete_table(u'authors')

        # Deleting model 'Source'
        db.delete_table(u'sources')

        # Removing M2M table for field authors on 'Source'
        db.delete_table('sources_authors')

        # Deleting model 'DataSet'
        db.delete_table(u'datasets')

        # Removing M2M table for field sources on 'DataSet'
        db.delete_table('datasets_sources')

        # Deleting model 'DataList'
        db.delete_table(u'datalists')

        # Deleting model 'TabulatedData'
        db.delete_table(u'tabulateddata')

        # Removing M2M table for field y on 'TabulatedData'
        db.delete_table('tabulateddata_y')

        # Removing M2M table for field x on 'TabulatedData'
        db.delete_table('tabulateddata_x')

        # Removing M2M table for field accuracy on 'TabulatedData'
        db.delete_table('tabulateddata_accuracy')


    models = {
        'node.author': {
            'Meta': {'object_name': 'Author', 'db_table': "u'authors'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'node.collision': {
            'Meta': {'object_name': 'Collision', 'db_table': "u'collisions'"},
            'collision_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.CollisionType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'product'", 'to': "orm['node.SpeciesState']"}),
            'reactant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reactant'", 'to': "orm['node.SpeciesState']"})
        },
        'node.collisiontype': {
            'Meta': {'object_name': 'CollisionType', 'db_table': "u'collisiontypes'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'iaea_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vamdc_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'node.crosssectiontype': {
            'Meta': {'object_name': 'CrossSectionType', 'db_table': "u'crosssectiontypes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'node.datalist': {
            'Meta': {'object_name': 'DataList', 'db_table': "u'datalists'"},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data_values': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'node.dataset': {
            'Meta': {'object_name': 'DataSet', 'db_table': "u'datasets'"},
            'collision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.Collision']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'data_sets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.Source']"})
        },
        'node.source': {
            'Meta': {'object_name': 'Source', 'db_table': "u'sources'"},
            'article_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sources'", 'symmetrical': 'False', 'to': "orm['node.Author']"}),
            'bibtex': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'digital_object_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_begin': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'page_end': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'source_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'source_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'node.species': {
            'Meta': {'object_name': 'Species', 'db_table': "u'species'"},
            'cas': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'chemical_formula': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inchi': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'inchikey': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'species_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.SpeciesType']"})
        },
        'node.speciesstate': {
            'Meta': {'object_name': 'SpeciesState', 'db_table': "u'speciesstates'"},
            'configuration': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'j': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['node.Species']"}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'treshold': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'x': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tabulated_data_x'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.DataList']"}),
            'y': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tabulated_data_y'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['node.DataList']"})
        }
    }

    complete_apps = ['node']
