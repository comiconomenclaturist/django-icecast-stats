from django.contrib import admin
from .models import Source


class SourceAdmin(admin.ModelAdmin):
    list_display = (
        "stream",
        "timestamp",
        "connection",
    )


admin.site.register(Source, SourceAdmin)
