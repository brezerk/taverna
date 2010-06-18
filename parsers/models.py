from django.db import models

# Create your models here.

class Installed(models.Model):
    name = models.CharField(max_length=32)
    function = models.CharField(max_length=32, null=True, blank=True)
    def __unicode__(self):
        return self.name
