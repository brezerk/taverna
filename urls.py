from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^taverna/', include('taverna.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),

    (r'^$', 'blogs.views.index'),
    
    (r'^register/$', 'userauth.views.registerUser'),
    (r'^login.html$', 'userauth.views.loginUser'),
    (r'^logout/$', 'userauth.views.logoutUser'),
    (r'^(?P<username>\w+)/$', 'blogs.views.viewBlog'),
    (r'^(?P<username>\w+)/blog/addtopic/$', 'blogs.views.addTopic'),
    (r'^(?P<username>\w+)/profile/$', 'userauth.views.viewProfile'),
    (r'^(?P<username>\w+)/edit/$', 'userauth.views.editProfile'),
    (r'^(?P<username>\w+)/blog/edit/$', 'blogs.views.editBlog'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
