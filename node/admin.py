from django.contrib import admin
from .models import \
    Species, \
    SpeciesType, \
    SpeciesState, \
    Collision, \
    CollisionType, \
    DataSet, \
    TabulatedData, \
    CrossSectionType, \
    DataList, \
    Source, \
    Author \

class SourceAdmin(admin.ModelAdmin):
    filter_horizontal = ("authors",)

admin.site.register(Species)
admin.site.register(SpeciesType)
admin.site.register(SpeciesState)
admin.site.register(Collision)
admin.site.register(CollisionType)
admin.site.register(DataSet)
admin.site.register(TabulatedData)
admin.site.register(CrossSectionType)
admin.site.register(DataList)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author)
