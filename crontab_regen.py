# -*- coding: utf-8 -*-

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from userauth.models import User, Profile
from django.conf import settings

if __name__=="__main__":
    users = Profile.objects.filter(karma__lt = settings.FORCE_REGEN['BORDER'], buryed = False)
    for user in users:
        user.karma += settings.FORCE_REGEN['RATE']
        user.force = user.karma
        user.save()

