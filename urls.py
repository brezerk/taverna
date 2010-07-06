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
    (r'^blog/libpost-new-1.so$', 'blogs.views.addPost'),
    (r'^blog/libsettings-0.so$', 'blogs.views.editBlog'),
    (r'^blog/libpost-0.so.(?P<postid>\d+)$', 'blogs.views.viewPost'),

    (r'^libforum-1.so$', 'forum.views.index'),
    (r'^libforum-1/(?P<forum_id>\d+).so$', 'forum.views.forum'),
    (r'^libforum-1/posting.so$', 'forum.views.reply'),
    (r'^libforum-1/reply-(?P<post_id>\d+).so$', 'forum.views.reply'),
    (r'^libforum-1/thread-(?P<post_id>\d+).so$', 'forum.views.thread'),
    (r'^libforum-1/create.so$', 'forum.views.forum_create'),

    (r'^pam/liblogout.so$', 'userauth.views.logoutUser'),
    (r'^pam/libprofile-0.so.(?P<userid>\d+)$', 'userauth.views.viewProfile'),
    (r'^pam/libprofile-edit-0.so$', 'userauth.views.editProfile'),

    (r'^login/$', 'userauth.views.openidChalange'),
    (r'^login/finish/$', 'userauth.views.openidFinish'),

    (r'^blog/libblog-0.so.(?P<blogid>\d+)$', 'blogs.views.viewBlog'), # WARNING: this one MUST be last

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
