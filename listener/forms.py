from django import forms
from django.contrib.postgres.forms import DateTimeRangeField
from .models import Station, Region
from django_filters.filters import TimeRangeField


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
	

class TimeRangeWidget(forms.widgets.MultiWidget):
	def __init__(self, attrs=None, dt=None, mode=0):
		widgets = (
			forms.widgets.TimeInput(attrs={'size': 5, 'class': 'exclude'}), 
			forms.widgets.TimeInput(attrs={'size': 5, 'class': 'exclude'}),
			)
		super(TimeRangeWidget, self).__init__(widgets, attrs)


class ListenerForm(forms.Form):
	station 	= forms.ModelChoiceField(queryset=Station.objects.all(), required=False)
	region 		= forms.ModelChoiceField(queryset=Region.objects.all(), required=False)
	referrer	= forms.ChoiceField(required=False)
	datepicker	= forms.CharField(label='Period', widget=forms.TextInput(attrs={'size': 32, 'class': 'exclude'},), required=False)
	period		= DateTimeRangeField(widget=forms.widgets.SplitHiddenDateTimeWidget())
	dom 		= forms.ChoiceField(label='Occurrence', choices=DOM_CHOICES, required=False)
	dow			= forms.ChoiceField(label='Weekday', choices=DOW_CHOICES, required=False)
	timepicker	= forms.CharField(label='Slot', widget=TimeRangeWidget, required=False)
	slot		= TimeRangeField(widget=forms.widgets.SplitHiddenDateTimeWidget(), required=False)

	def clean(self):
		if 'referrer' in self._errors:
			del self._errors['referrer']
		return self.cleaned_data