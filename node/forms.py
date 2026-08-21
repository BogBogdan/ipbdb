from django import forms
from node.models import *

class Search_form(forms.Form):
    CollisionTypes = forms.ModelChoiceField(queryset = CollisionType.objects.all(), label='Collision Type', to_field_name='iaea_code')
    Species = forms.ModelChoiceField(queryset = Species.objects.none(), widget = forms.Select(attrs={'disabled':'disabled'}))
    SpeciesStates = forms.ModelChoiceField(queryset = SpeciesState.objects.none(), widget = forms.Select(attrs={'disabled':'disabled'}), label='Species State (product)')
    CrossSectionTypes = forms.ModelChoiceField(queryset = CrossSectionType.objects.none(), widget = forms.Select(attrs={'disabled':'disabled'}), label='Cross Section Type')
