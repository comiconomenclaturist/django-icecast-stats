from django.contrib import admin
from .models import Source


class SourceAdmin(admin.ModelAdmin):
    list_display = (
        "stream",
        "timestamp",
        "connection",
    )
    list_filter = ("stream__station", "stream__mountpoint", "timestamp")


admin.site.register(Source, SourceAdmin)
