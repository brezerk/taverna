# -*- coding: utf-8 -*-

from django.contrib import admin
from taverna.parsers.models import Installed

class InstalledAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


admin.site.register(Installed, InstalledAdmin)


