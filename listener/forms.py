from django import forms
from .models import Listener, Stream, ListenerAggregate


class ListenerForm(forms.ModelForm):
	class Meta:
		model = Listener
		fields = '__all__'


class ListenerAggregateForm(forms.ModelForm):
	station = forms.ChoiceField(choices=[('A', 'All')] + Stream.STATION_CHOICES)
	period = forms.CharField(widget=forms.TextInput(attrs={'size': 35}))

	class Meta:
		model = ListenerAggregate
		fields = ('station', 'period',)

		