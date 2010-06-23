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
from util import rr

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

import re
import cracklib
import hashlib

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

class RegisterForm(forms.Form):
    username = forms.CharField(required=True, max_length=16)
    email = forms.EmailField(required=True, max_length=32)
    rpassword = forms.CharField(required=True, max_length=32,
                                widget=forms.PasswordInput
                               )
    password = forms.CharField(required=True, max_length=32,
                               widget=forms.PasswordInput
                              )
    recaptcha_response_field = forms.CharField(required=True)
    recaptcha_challenge_field = forms.CharField(required=True)

    captchaHTML = captcha.displayhtml(public_key = settings.RECAPTCHA_PUBLIC_KEY,
                use_ssl = False,
                error = None,
                theme = "clean")
    remoteip = None
    response = None
    challange = None

    def clean_password(self):
        password = self.cleaned_data['password']
        try:
            cracklib.VeryFascistCheck(password)
        except ValueError:
            raise forms.ValidationError(_("Password is too simple."))

        rpassword = self.cleaned_data['rpassword']
        if password != rpassword:
            raise forms.ValidationError(_("Passwords do not match."))
        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            if User.objects.get(email__exact=email):
                raise forms.ValidationError(_("E-Mail already exists."))
        except User.DoesNotExist:
            pass
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            if User.objects.get(username__exact=username):
                raise forms.ValidationError(_("Login already in use"))
        except User.DoesNotExist:
            pass

        return username

    def clean_recaptcha_challenge_field(self):
        try:
            challenge = self.cleaned_data['recaptcha_challenge_field']
            response = self.cleaned_data['recaptcha_response_field']

            cResponse = captcha.submit(
                      challenge,
                      response,
                      settings.RECAPTCHA_PRIVATE_KEY,
                      self.remoteip)
            if not cResponse.is_valid:
                raise forms.ValidationError(_("Wrong captcha"))
            return True

        except KeyError:
            raise forms.ValidationError(_("Wrong captcha"))

    def setReCaptchaVals(self, remoteip):
        self.remoteip = remoteip


    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        mailhash = hashlib.md5(email).hexdigest()
        user = User(username=username, email=email,
                    is_staff=False, is_active=True,
                    is_superuser=False)
        user.set_password(password)
        user.save()
        profile = Profile(user=user, photo=mailhash)
        profile.save()

        try:
            blog = Blog.objects.get(owner = user)
        except Blog.DoesNotExist:
            blog = Blog(name = "%s's blog" % user)
            blog.owner = user
            blog.save()
        #FIXME: We need to accign group for new users, also, groups might be created at site startup

@csrf_protect
def registerUser(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        form.setReCaptchaVals(request.META['REMOTE_ADDR'])
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = RegisterForm()

    return render_to_response("userauth/register.html", {'form': form},
                              context_instance=RequestContext(request)
                             )
@rr('userauth/login.html')
def loginUser(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == 'GET':
        return {'form': AuthenticationForm()}
    elif request.method == 'POST':
        user = authenticate(username = request.POST["username"],
            password = request.POST["password"])
        if user:
            login(request, user)
            return(HttpResponseRedirect('/'))
        else:
            return {'form': AuthenticationForm()}

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required(redirect_field_name='login.html')
def viewProfile(request, username):
    try:
        user_info = User.objects.get(username__exact=username)
        user_profile = Profile.objects.get(user=user_info)
        try:
            user_blog = Blog.objects.get(owner=user_info)
        except Blog.DoesNotExist:
            user_blog = None
        return render_to_response("userauth/profile.html", {'user_info': user_info,
                                  'user_profile': user_profile,
                                  'user_blog': user_blog},
                                  context_instance=RequestContext(request)
                                 )
    except (User.DoesNotExist, Profile.DoesNotExist):
        return HttpResponseRedirect('/')

@login_required(redirect_field_name='/login')
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
