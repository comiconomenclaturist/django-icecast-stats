from django.utils import timezone
from rest_framework import serializers
from .models import *
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
import re


class ListenerSerializer(serializers.ModelSerializer):
	country = CountryField()
	user_agent = serializers.CharField(source='user_agent.name', read_only=True)
	stream = serializers.CharField(source='stream.mountpoint', read_only=True)

	class Meta:
		model = Listener
		fields = ('ip_address', 'stream', 'connected_at', 'disconnected_at', 'duration', 'user_agent', 'country', 'city',)


class StreamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Stream
		fields = ('mountpoint',)


class DateTimeTZField(serializers.DateTimeField):
	def to_representation(self, value):
		value = timezone.localtime(value)
		return super(DateTimeTZField, self).to_representation(value)


class CountSerializer(serializers.ModelSerializer):
	period = serializers.DateTimeField()
	stream = serializers.ReadOnlyField()
	count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Listener
		fields = ('period', 'stream', 'count',)


class HoursSerializer(serializers.ModelSerializer):
	period = serializers.DateTimeField()
	stream = serializers.ReadOnlyField()
	hours = serializers.FloatField(read_only=True)

	class Meta:
		model = Listener
		fields = ('period', 'stream', 'hours', )


class CountriesSerializer(serializers.ModelSerializer):
	country = CountryField(country_dict=True)
	country__name = serializers.ReadOnlyField()
	count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Listener
		fields = ('country', 'country__name', 'count',)

	def to_representation(self, instance):
		data = super().to_representation(instance)
		if not data['country']:
			data['country'] = {'name': 'Unknown', 'code': ''}
		return data


class RefererSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField(read_only=True)
	domain = serializers.ReadOnlyField()

	class Meta:
		model = Listener
		fields = ('domain', 'count',)

	# def to_representation(self, instance):
	# 	data = super().to_representation(instance)
	# 	data['referer'] = re.sub(r'(?:.*://)?([^/?]+).*', r'\1', data['referer'])
	# 	return data

