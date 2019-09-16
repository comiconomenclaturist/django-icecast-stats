from django.contrib import admin
from .models import Stream, Station, Listener, ListenerAggregate, IngestParameters


class ListenerAdmin(admin.ModelAdmin):
	raw_id_fields = ('user_agent',)
	list_display = ('ip_address', 'stream', 'session', 'duration', 'user_agent', 'country',)
	list_editable = ()
	search_fields = ('ip_address',)
	list_filter = ('stream', 'user_agent__device__brand', 'user_agent__is_bot',)


class StreamAdmin(admin.ModelAdmin):
	list_display = ('mountpoint', 'station', 'bitrate',)


class StationAdmin(admin.ModelAdmin):
	list_display = ('name',)


class ListenerAggregateAdmin(admin.ModelAdmin):
	list_display = ('period', 'stream', 'count', 'duration',)


admin.site.register(Stream, StreamAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Listener, ListenerAdmin)
admin.site.register(ListenerAggregate, ListenerAggregateAdmin)
admin.site.register(IngestParameters)
