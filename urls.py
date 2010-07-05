from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^$', 'blogs.views.index'),
    (r'^blogs/$', 'blogs.views.viewBlogsList'),
    (r'^blogs/public/$', 'blogs.views.viewBlogsPublicList'),
    (r'^blogs/users/$', 'blogs.views.viewBlogsUserList'),
    (r'^blogs/users/(?P<page>\w+)/$', 'blogs.views.viewBlogsUserList'),
    (r'^blog-addtopic.html$', 'blogs.views.addTopic'),
    (r'^blog-settings.html$', 'blogs.views.editBlog'),
    (r'^(.+)/(?P<post>\w+)$', 'blogs.views.viewPost'),

    (r'^forums.html$', 'forum.views.index'),
    (r'^forums/thread/(?P<post_id>\d+).html$', 'forum.views.thread'),
    (r'^forums/reply/(?P<forum_id>\d+).html$', 'forum.views.reply'),
    (r'^forums/thread/reply/(?P<post_id>\d+).html$', 'forum.views.reply'),
    (r'^forums/(?P<forum_id>\d+).html$', 'forum.views.forum'),
    (r'^forum_create/$', 'forum.views.forum_create'),

    (r'^logout.so$', 'userauth.views.logoutUser'),
    (r'^(?P<username>\w+)/profile.html$', 'userauth.views.viewProfile'),
    (r'^profile-edit.html$', 'userauth.views.editProfile'),
    (r'^(?P<username>\w+)/edit/$', 'userauth.views.editProfile'),

    (r'^login/$', 'userauth.views.openidChalange'),
    (r'^login/finish/$', 'userauth.views.openidFinish'),

    (r'^(?P<blog_slug>\w+)/$', 'blogs.views.viewBlog'), # WARNING: this one MUST be last

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login.html"
