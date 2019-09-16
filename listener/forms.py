from django import forms
from .models import Listener, Stream, Station, ListenerAggregate


class ListenerForm(forms.ModelForm):
	class Meta:
		model = Listener
		fields = '__all__'


class ListenerAggregateForm(forms.ModelForm):
	station = forms.ModelChoiceField(queryset=Station.objects.all())
	period = forms.CharField(widget=forms.TextInput(attrs={'size': 35}))

	class Meta:
		model = ListenerAggregate
		fields = ('station', 'period',)

		