from django.db import models

class Device(models.Model):
	family	= models.CharField(max_length=255)
	brand	= models.CharField(max_length=255, null=True)
	model	= models.CharField(max_length=255, null=True)

	class Meta:
		unique_together = ['family', 'brand', 'model']
		ordering = ('family', 'brand', 'model',)

	def __str__(self):
		return ', '.join(filter(None, (self.family, self.brand, self.model)))

class OS(models.Model):
	family	= models.CharField(max_length=255)
	version = models.CharField(max_length=255)

	class Meta:
		unique_together = ('family', 'version',)
		verbose_name = 'OS'
		verbose_name_plural = "OSs"
		ordering = ('family', 'version')

	def __str__(self):
		return ', '.join(filter(None, (self.family, self.version)))

class Browser(models.Model):
	family	= models.CharField(max_length=255)
	version	= models.CharField(max_length=255)

	class Meta:
		unique_together = ['family', 'version']
		ordering = ('family', 'version')

	def __str__(self):
		return ', '.join(filter(None, (self.family, self.version)))

class UserAgent(models.Model):
	string		= models.CharField(max_length=255)
	device		= models.ForeignKey(Device, blank=True, null=True, on_delete=models.CASCADE)
	os			= models.ForeignKey(OS, blank=True, null=True, on_delete=models.CASCADE)
	browser		= models.ForeignKey(Browser, blank=True, null=True, on_delete=models.CASCADE)
	is_mobile	= models.BooleanField(default=False)
	is_tablet	= models.BooleanField(default=False)
	is_bot		= models.BooleanField(default=False)

	class Meta:
		unique_together = ('string', 'device', 'os', 'browser',)
		verbose_name = 'User Agent'

	@property
	def name(self):
		return ', '.join((f.__str__() for f in filter(None, (self.device, self.os, self.browser)))) or self.string

	def __str__(self):
		return self.name
		
