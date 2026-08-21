from django.db import models
import datetime

class SpeciesType(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return "%s" % (self.name, )
    def __unicode__(self):
        return "%s" % (self.name, )

    class Meta:
        db_table = u'speciestypes'

class Species(models.Model):
    name = models.CharField(max_length=32, db_index=True)
    inchi = models.CharField(max_length=256)
    inchikey = models.CharField(max_length=128)
    chemical_formula = models.CharField(max_length=128)
    stoichiometric_formula = models.CharField(max_length=128, null=True, blank=True)
    cas = models.CharField(max_length=128, null=True, blank=True)
    species_type = models.ForeignKey(SpeciesType, on_delete=models.CASCADE)
    nuclear_charge = models.CharField(max_length=32, null=True, blank=True)
    ion_charge = models.IntegerField(default=0)
    molecular_weight = models.FloatField(null=True, blank=True, error_messages={'invalid':"Please enter a valid float number"})
    def __str__(self):
        return "%s: %s" % (self.name, self.chemical_formula)
    def __unicode__(self):
        return "%s: %s" % (self.name, self.chemical_formula )
    class Meta:
        db_table = u'species'
        verbose_name_plural = 'Species'

class SpeciesState(models.Model):
    configuration = models.CharField(max_length=512)
    treshold = models.FloatField(null=True, blank=True, error_messages={'invalid':"Please enter a valid float number"})
    treshold_unit = models.CharField(max_length=32, null=True, blank=True)
    j = models.CharField(max_length=128, null=True, blank=True)
    term = models.CharField(max_length=128, null=True, blank=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    description = models.CharField(max_length=256, null=True, blank=True)
    def __str__(self):
        return "%s - %s - %s" % (self.species.name, self.description, self.treshold )
    def __unicode__(self):
        return "%s - %s - %s" % (self.species.name, self.description, self.treshold )
#    def XML(self):
#	return '<AtomicState></AtomicState>'
    class Meta:
        db_table = u'speciesstates'

class CollisionType(models.Model):
    name = models.CharField(max_length=64)
    iaea_code = models.CharField(max_length=64, null=True, unique=True, error_messages={'unique':"This code is already associated with another collision type"})
    vamdc_code = models.CharField(max_length=64, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return "%s" % (self.name, )
    def __unicode__(self):
        return "%s" % (self.name, )

    class Meta:
        db_table = u'collisiontypes'

class Collision(models.Model):
    reactant = models.ForeignKey(SpeciesState, related_name="reactant", on_delete=models.CASCADE)
    product = models.ForeignKey(SpeciesState, related_name="product", on_delete=models.CASCADE)
    collision_type = models.ForeignKey(CollisionType, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    lastmodified = models.DateTimeField(default=datetime.datetime.now())
    def __str__(self):
        return "id: %s %s" % (self.id, self.description )
    def __unicode__(self):
        return "id: %s %s" % (self.id, self.description )

    class Meta:
        db_table = u'collisions'

class CrossSectionType(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=64, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return "%s" % (self.name, )
    def __unicode__(self):
        return "%s" % (self.name, )

    class Meta:
        db_table = u'crosssectiontypes'

class Author(models.Model):
    name = models.CharField(max_length=128)
    institution = models.CharField(max_length=256, null=True, blank=True)
    def __str__(self):
        return "%s" % (self.name)
    def __unicode__(self):
        return "%s" % (self.name)

    class Meta:
        db_table= u'authors'
        ordering = ['name']

class Source(models.Model):
    CATEGORY_CHOICES = (
            ('book', 'book'),
            ('database', 'database'),
            ('journal', 'journal'),
            ('preprint', 'preprint'),
            ('proceedings', 'proceedings'),
            ('report', 'report'),
            ('thesis', 'thesis'),
            ('private communication', 'private communication'),
            ('vamdc node', 'vamdc node'),
            )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='journal')
    article_number = models.CharField(max_length=128, null=True, blank=True, help_text="""Article number, journal-specific article identifier, may contain any string""")
    digital_object_id = models.CharField(max_length=128, null=True, blank=True, help_text="""Digital Object Identifier. Example: doi:10.1016/j.adt.2007.11.003""")
    title = models.CharField(max_length=128, help_text="""Title""")
    source_id = models.CharField(max_length=128, null=True, blank=True)
    publisher = models.CharField(max_length=256, null=True, blank=True, help_text="""Publisher of a bibliographic reference. Example: IOP Publishing Ltd""")
    authors = models.ManyToManyField(Author, related_name="sources")
    uri = models.CharField(max_length=256, null=True, blank=True, help_text="""A Uniform Resource Identifier of a bibliographic reference. Example: http://www.iop.org/EJ/abstract/0953-4075/41/10/105002""")
    page_begin = models.CharField(max_length=16, null=True, blank=True, help_text="""Initial page of a bibliographic reference. Example: 22""")
    page_end = models.CharField(max_length=16, null=True, blank=True, help_text="""Final page of a bibliographic reference. Example: 23""")
    volume = models.CharField(max_length=128, null=True, blank=True, help_text="""Volume of the bibliographic reference. Example: 72A""")
    source_name = models.CharField(max_length=256, null=True, blank=True, help_text="""Bibliographic reference name. Example: Physical Review""")
    bibtex = models.CharField(max_length=1024, null=True, blank=True, help_text="""BibTeX representation of reference, for those who already have it in database""")
    comments = models.CharField(max_length=1024, null=True, blank=True)
    year = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        if len(self.title) > 0 :
            return "%s" % self.title
        return "id: %s %s" % (self.id, self.comments)
    def __unicode__(self):
        if len(self.title) > 0 :
            return "%s" % self.title
        return "id: %s %s" % (self.id, self.comments)

    class Meta:
        db_table= u'sources'

class DataSet(models.Model):
    collision = models.ForeignKey(Collision, null=True, blank=True, on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source, related_name="data_sets", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return "id: %s %s" % (self.id, self.description)
    def __unicode__(self):
        return "id: %s %s" % (self.id, self.description)

    class Meta:
        db_table = u'datasets'


class DataList(models.Model):
    count =  models.IntegerField(null=True, blank=True)
    data_values = models.TextField(null=True, blank=True, help_text="""Space delimited values""")
    unit = models.CharField(max_length=16, null=True, blank=True)
    parameter = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    def __str__(self):
        return "id: %s %s" % (self.id, self.description)
    def __unicode__(self):
        return "id: %s %s" % (self.id, self.description)

    class Meta:
        db_table= u'datalists'

class TabulatedData(models.Model):
    dataset = models.ForeignKey(DataSet, null=True, blank=True, on_delete=models.CASCADE)
    cross_section_type = models.ForeignKey(CrossSectionType, on_delete=models.CASCADE)
    y = models.ManyToManyField(DataList, related_name="tabulated_data_y",
            help_text="""Data values.""", null=True, blank=True)
    x = models.ManyToManyField(DataList, related_name="tabulated_data_x",
            help_text="""Parameters(independent variables) values.""",
            null=True, blank=True)
    accuracy = models.ManyToManyField(DataList,
            related_name="tabulated_data_accuracy", null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return "id: %s %s" % (self.id, self.description)
    def __unicode__(self):
        return "id: %s %s" % (self.id, self.description)

    def XML(self):
        def axis_structure(axis):
            return '<%s units="%s" parameter="%s"><DataList count="%s">%s</DataList></%s>' % (axis, obj_.unit, obj_.parameter, str(obj_.count), obj_.data_values, axis)
        def y_structure(obj_y, obj_acc):
            return '<Y units="%s" parameter="%s"><DataList count="%s">%s</DataList><Accuracy relative="false" type="statistical"><ErrorList count="%s">%s</ErrorList></Accuracy></Y>' % (obj_y.unit, obj_y.parameter, str(obj_y.count), obj_y.data_values, str(obj_acc.count), obj_acc.data_values)
        xml = '<TabulatedData>'
        for source in self.dataset.sources.all():
            xml += '<SourceRef>BIPBemol-%s</SourceRef>' % source.source_id
        for obj_ in self.x.all():
            xml += axis_structure('X')
        if self.accuracy.all():
            xml += y_structure(self.y.all()[0], self.accuracy.all()[0])
        else:
            for obj_ in self.y.all():
                xml += axis_structure('Y')
        xml += '</TabulatedData>'
        return xml

    class Meta:
        db_table= u'tabulateddata'
        verbose_name_plural = 'Tabulated data'
