from rest_framework import serializers
from listener.models import Listener


class BrowserSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)
    family = serializers.ReadOnlyField(source="user_agent__browser__family")

    class Meta:
        model = Listener
        fields = (
            "family",
            "count",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data["family"]:
            data["family"] = "Unknown"
        return data
