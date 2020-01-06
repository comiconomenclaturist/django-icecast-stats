from django import forms
from .models import Listener, Station, Region


class ListenerForm(forms.Form):
	station = forms.ModelChoiceField(queryset=Station.objects.all())
	region = forms.ModelChoiceField(queryset=Region.objects.all())
	period = forms.CharField(widget=forms.TextInput(attrs={'size': 28}))	

