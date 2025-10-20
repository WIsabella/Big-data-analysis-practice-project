from django import forms

'''根据网页和需求重写'''
class BacteriaSearchForm(forms.Form):
    taxonomic_unit = forms.CharField(label="分类单元", required=False,
                            widget=forms.TextInput(attrs={"placeholder": "输入分类单元"}))
    # 分离日期 = forms.CharField(label="分离日期", required=False,
    #                           widget=forms.TextInput(attrs={"placeholder": "输入分离日期"}))
    # Closest_species = forms.CharField(label="Closest species", required=False,
    #                                  widget=forms.TextInput(attrs={"placeholder": "输入 Closest species"}))
    # 分离源 = forms.CharField(label="分离源", required=False,
    #                        widget=forms.TextInput(attrs={"placeholder": "输入分离源"}))
    # 需氧性 = forms.CharField(label="需氧性", required=False,
    #                        widget=forms.TextInput(attrs={"placeholder": "输入需氧性"}))