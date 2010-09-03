# -*- coding: utf-8 -*-

# Copyright (C) 2010 by Alexey S. Malakhov <brezerk@gmail.com>
#                       Opium <opium@jabber.com.ua>
#
# This file is part of Taverna
#
# Taverna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taverna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Taverna.  If not, see <http://www.gnu.org/licenses/>.

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from userauth.models import User, Profile
from django.conf import settings
from django.db.models import F

if __name__=="__main__":
    users = Profile.objects.filter(karma__lt = settings.FORCE_REGEN['BORDER'], buryed = False)
    users.update(karma = F('karma') + 1)

    users = Profile.objects.filter(force__lt = F('karma'), buryed = False)
    users.update(force = F('force') + 1)
