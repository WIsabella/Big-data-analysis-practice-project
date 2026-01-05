from django import forms

'''提交的搜索关键词表单'''
class BacteriaSearchForm(forms.Form):
    taxonomic_unit = forms.CharField(required=False,max_length=100)
    species = forms.CharField(required=False,max_length=100)
    health_status = forms.CharField(required=False,max_length=100)
    is_sequenced = forms.BooleanField(required=False)
    has_metabolomics_data = forms.BooleanField(required=False)