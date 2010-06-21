from django.contrib import admin
from django.contrib.auth.models import User
from models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'karma', 'jabber', 'website',)

admin.site.register(Profile, ProfileAdmin)
