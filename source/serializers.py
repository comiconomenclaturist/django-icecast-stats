from rest_framework import serializers
from .models import Disconnection


class DisconnectionSerializer(serializers.ModelSerializer):
    stream = serializers.CharField(source="stream.mountpoint", read_only=True)

    class Meta:
        model = Disconnection
        fields = (
            "stream",
            "connected_at",
            "disconnected_at",
        )
