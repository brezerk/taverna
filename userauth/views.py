# -*- coding: utf-8 -*-
# Create your views here.

#from librecaptcha import librecaptcha
from recaptcha.client import captcha
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from userauth.models import Profile
from blogs.models import Blog
from util import rr, getViewURL, getOpenIDStore

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

import re
import cracklib
import hashlib

import openid

from openid.store import filestore
from openid.consumer import consumer

from django.template.defaultfilters import slugify

class ProfileForm(forms.Form):
    first_name = forms.CharField(required=False, max_length=32)
    last_name = forms.CharField(required=False, max_length=32)
    email = forms.EmailField(required=True, max_length=32)
    jabber = forms.EmailField(required=False, max_length=32)
    location = forms.CharField(required=False, max_length=32)
    website = forms.CharField(required=False, max_length=32)
    sign = forms.CharField(required=False, max_length=256, widget=forms.Textarea(attrs={'rows':'4'}))
    rnewpassword = forms.CharField(required=False, max_length=32, widget=forms.PasswordInput)
    newpassword = forms.CharField(required=False, max_length=32, widget=forms.PasswordInput)
    password = forms.CharField(required=True, max_length=32, widget=forms.PasswordInput)
    user = None

    def setUser(self, user):
        self.user = user

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            if User.objects.filter(email__exact=email).exclude(username=self.user.username):
                raise forms.ValidationError(_("E-Mail already exists."))
        except User.DoesNotExist:
            pass
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(_("Current password is wrong."))
        return password

    def clean_newpassword(self):
        newpassword = self.cleaned_data['newpassword']
        rnewpassword = self.cleaned_data['rnewpassword']
        if newpassword:
            if newpassword != rnewpassword:
                raise forms.ValidationError(_("Passwords do not match."))
            try:
                cracklib.VeryFascistCheck(newpassword)
            except ValueError:
                raise forms.ValidationError(_("Password is too simple."))
        return newpassword

    def save(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']
        jabber = self.cleaned_data['jabber']
        website = self.cleaned_data['website']
        sign = self.cleaned_data['sign']
        location = self.cleaned_data['location']

        User.objects.filter(username=self.user.username).update(first_name=first_name,last_name=last_name,email=email)
        mailhash = hashlib.md5(email).hexdigest()
        Profile.objects.filter(user=self.user).update(jabber=jabber, website=website, sign=sign, location=location, photo=mailhash)

        newpassword = self.cleaned_data['newpassword']

        if newpassword:
           self.user.set_password(newpassword)
           self.user.save()

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required()
@rr ('userauth/profile.html')
def viewProfile(request, username):
    try:
        user_info = User.objects.get(username__exact=username)
        user_profile = Profile.objects.get(user=user_info)
        try:
            user_blog = Blog.objects.get(owner=user_info)
        except Blog.DoesNotExist:
            user_blog = None
        return {'user_info': user_info,
                'user_profile': user_profile,
                'user_blog': user_blog}

    except (User.DoesNotExist, Profile.DoesNotExist):
        return HttpResponseRedirect('/')

@login_required()
@rr ('userauth/settings.html')
def editProfile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        form.setUser(request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("userauth.views.viewProfile", args=[request.user.username]))
    else:
        profile = Profile.objects.get(user=request.user)
        form = ProfileForm({'first_name': request.user.first_name,
                            'last_name': request.user.last_name,
                            'email': request.user.email,
                            'jabber': profile.jabber,
                            'website': profile.website,
                            'location': profile.location,
                            'sign': profile.sign,
                          })
    return {'form': form}

@rr ('userauth/openid.html')
def openidChalange(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    class OpenidForm(forms.Form):
        openid = forms.CharField(required=True, max_length=32)

    form = None

    if (request.POST):
        form = OpenidForm(request.POST)

        store = getOpenIDStore("/tmp/taverna_openid", "c_")
        c = consumer.Consumer(request.session, store)
        openid_url = request.POST['openid']

        try:
            auth_request = c.begin(openid_url)
        except consumer.DiscoveryFailure, exc:
            error = "OpenID discovery error: %s" % str(exc)
            return {'form': form, 'error': error}

        if auth_request.shouldSendRedirect():
            trust_root = getViewURL(request, openidChalange)
            redirect_to = getViewURL(request, openidFinish)
            return HttpResponseRedirect(auth_request.redirectURL(trust_root, redirect_to))
    else:
        form = OpenidForm()
    return {'form': form}

@rr ('userauth/openid.html')
def openidFinish(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    form = None
    error = None
    request_args = request.GET

    store = getOpenIDStore("/tmp/taverna_openid", "c_")
    c = consumer.Consumer(request.session, store)

    return_to = getViewURL(request, openidFinish)
    response = c.complete(request_args, return_to)

    if response.status == consumer.SUCCESS:
        openid_hash=hashlib.md5(response.getDisplayIdentifier()).hexdigest()

        try:
            profile = Profile.objects.get(openid_hash = openid_hash)
            username = profile.user.username
            password = profile.user.password
            user = authenticate(username=username)
            if user is not None:
                login(request, user)
        except Profile.DoesNotExist:
            user = User(username = slugify(response.getDisplayIdentifier()[7:-1]),
                        is_staff = False, is_active = True,
                        is_superuser = False)
            user.save()
            profile = Profile(user = user, photo = "", openid_hash = openid_hash)
            profile.save()
            try:
                blog = Blog.objects.get(owner = user)
            except Blog.DoesNotExist:
                blog = Blog(owner = user)
                blog.save()

            auth = authenticate(username=user.username)
            if user is not None:
                login(request, auth)

        return HttpResponseRedirect("/")
    else:
        error = "Verification of %s failed: %s" % (response.getDisplayIdentifier(), response.message)

    return {'from': form, 'error': error}

