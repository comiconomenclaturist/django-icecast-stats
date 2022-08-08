from django.contrib import admin
from .models import Disconnection


class DisconnectionAdmin(admin.ModelAdmin):
    list_display = (
        "stream",
        "disconnected_at",
        "connected_at",
    )


admin.site.register(Disconnection, DisconnectionAdmin)
