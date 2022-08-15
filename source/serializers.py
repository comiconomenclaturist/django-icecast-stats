from rest_framework import serializers
from listener.models import Stream
from .models import Source


class ConnectionSerializer(serializers.ModelSerializer):
    x = serializers.DateTimeField(source="timestamp")
    y = serializers.SerializerMethodField(method_name="convert_boolean")

    def convert_boolean(self, instance):
        return 1 if instance.connection else 0

    class Meta:
        model = Source
        fields = (
            "x",
            "y",
        )


class SourceSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="mountpoint")
    data = ConnectionSerializer(source="connections", many=True)

    class Meta:
        model = Stream
        fields = (
            "label",
            "data",
        )
