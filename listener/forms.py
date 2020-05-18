from django import forms
from django.contrib.postgres.forms import DateTimeRangeField
from .models import Station, Region

DOW_CHOICES = (
	('', '---------'),
	('0', 'Monday'),
	('1', 'Tuesday'),
	('2', 'Wednesday'),
	('3', 'Thursday'),
	('4', 'Friday'),
	('5', 'Saturday'),
	('6', 'Sunday'),
	)

DOM_CHOICES = (
	('', 'Every'),
	('1', '1st'),
	('2', '2nd'),
	('3', '3rd'),
	('4', '4th'),
	)

# class ListenerForm(forms.Form):
# 	station = forms.ModelChoiceField(queryset=Station.objects.all(), required=False)
# 	region 	= forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
# 	period 	= forms.CharField(widget=forms.TextInput(attrs={'size': 28}))
# 	dom 	= forms.ChoiceField(choices=DOM_CHOICES, label='', required=False)
# 	dow		= forms.ChoiceField(choices=DOW_CHOICES, label='', required=False)
# 	slot 	= forms.CharField(widget=forms.TextInput(attrs={'size': 28}), label='From', required=False)


class ListenerForm(forms.Form):
	station 	= forms.ModelChoiceField(queryset=Station.objects.all(), required=False)
	region 		= forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
	datepicker	= forms.CharField(label='Period', widget=forms.TextInput(attrs={'size': 28},), required=False)
	period		= DateTimeRangeField(widget=forms.widgets.SplitHiddenDateTimeWidget())
	dom 		= forms.ChoiceField(label='', choices=DOM_CHOICES, required=False)
	dow			= forms.ChoiceField(label='', choices=DOW_CHOICES, required=False)
	# timepicker	= forms.CharField(label='', widget=forms.TextInput(attrs={'size': 28},), required=False)
	# slot		= DateTimeRangeField(widget=forms.widgets.SplitHiddenDateTimeWidget())
	slot		= forms.CharField(label='', widget=forms.TextInput(attrs={'size': 28},), required=False)