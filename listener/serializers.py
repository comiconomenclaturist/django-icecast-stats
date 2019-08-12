from rest_framework import serializers
from .models import *
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin


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


class AggregateStreamSerializer(serializers.Serializer):
	mountpoint = serializers.CharField()
	count = serializers.IntegerField()
	hours = serializers.FloatField()
	

class AggregateSerializer(serializers.Serializer):
	period = serializers.DateTimeField()
	stream = AggregateStreamSerializer(many=True)


class CountStreamSerializer(serializers.Serializer):
	mountpoint = serializers.CharField()
	listeners = serializers.IntegerField()


class CountSerializer(serializers.Serializer):
	hour = serializers.DateTimeField()
	stream = CountStreamSerializer(many=True)


class HoursStreamSerializer(serializers.Serializer):
	mountpoint = serializers.CharField()
	listenerHours = serializers.DurationField()


class HoursSerializer(serializers.Serializer):
	hour = serializers.DateTimeField()
	stream = HoursStreamSerializer(many=True)


class CountriesSerializer(serializers.ModelSerializer):
	country = CountryField(country_dict=True)
	count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Listener
		fields = ('country', 'count',)

	def to_representation(self, instance):
		data = super().to_representation(instance)
		if not data['country']:
			data['country'] = "Unknown"
		return data


class RefererSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Listener
		fields = ('referer', 'count',)

	def to_representation(self, instance):
		data = super().to_representation(instance)
		if not data['referer']:
			data['referer'] = "Unknown"
		return data


class NewListenerSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField(read_only=True)
	station = serializers.ReadOnlyField(source='stream__station', read_only=True)
	hour = serializers.DateTimeField(read_only=True)

	class Meta:
		model = Listener
		fields = ('station', 'count', 'hour',)


