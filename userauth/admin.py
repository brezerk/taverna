from django.contrib import admin
from django.contrib.auth.models import User
from models import Profile, ReasonList

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'karma', 'jabber', 'website',)

admin.site.register(Profile, ProfileAdmin)

class ReasonAdmin(admin.ModelAdmin):
    list_display = ('description', 'cost',)

admin.site.register(ReasonList, ReasonAdmin)
