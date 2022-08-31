from django import forms
from .models import Search, Toilet



class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = ['address',]
       
class AddForm(forms.ModelForm):
    class Meta:
        model = Toilet
        fields = "__all__"

        #title = forms.CharField(label='title', max_length=200, required=True)
        #lat = forms.DecimalField(label='lat', decimal_places=6, required=True)

