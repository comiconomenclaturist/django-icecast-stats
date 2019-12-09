from django import forms
from .models import Listener, Station


class ListenerForm(forms.Form):
	station = forms.ModelChoiceField(queryset=Station.objects.all())
	period = forms.CharField(widget=forms.TextInput(attrs={'size': 28}))

