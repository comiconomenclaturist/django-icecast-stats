from django.contrib import admin
from .models import *


class UserAgentAdmin(admin.ModelAdmin):
	list_display = ('device', 'os', 'browser', 'is_mobile', 'is_tablet', 'is_bot', 'string',)
	list_filter = ('device__family', 'device__brand')

class DeviceAdmin(admin.ModelAdmin):
	list_display = ('family', 'brand', 'model')

class OSAdmin(admin.ModelAdmin):
	list_display = ('family', 'version')

class BrowserAdmin(admin.ModelAdmin):
	list_display = ('family', 'version')


admin.site.register(UserAgent, UserAgentAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(OS, OSAdmin)
admin.site.register(Browser, BrowserAdmin)
