from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from taverna.blog.feeds import RssBlogTraker, AtomBlogTraker, RssBlog, AtomBlog
from taverna.blog.sitemaps import BlogSitemap

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    (r'^$', 'blog.views.index'),
    (r'^blog/libblog-(?P<page>\d+).so$', 'blog.views.index'),

    (r'^blog/libblog-0.so.(?P<blog_id>\d+)$', 'blog.views.view'),
    (r'^blog/libblog-(?P<page>\d+).so.(?P<blog_id>\d+)$', 'blog.views.view'),

    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),
    (r'^blogs/$', 'blog.views.list'),
    (r'^blogs/public/$', 'blog.views.list_public'),
    (r'^blogs/users/$', 'blog.views.list_users'),
    (r'^blog/libpost-new-1.so$', 'blog.views.post_add'),
    (r'^blog/libsettings-0.so$', 'blog.views.settings'),
    (r'^blog/libpost-0.so.(?P<post_id>\d+)$', 'blog.views.post_view'),
    (r'^blog/libpost-(?P<page>\d+).so.(?P<post_id>\d+)$', 'blog.views.post_view'),
    (r'^blog/libtag-0.so.(?P<tag_id>\d+)$', 'blog.views.tags_search'),
    (r'^blog/libtag-(?P<page>\d+).so.(?P<tag_id>\d+)$', 'blog.views.tags_search'),
    (r'^blog/libcomment-0.so.(?P<post_id>\d+)$', 'blog.views.post_comment'),

    (r'^forum.so$', 'forum.views.index'),
    (r'^forum.so.(?P<forum_id>\d+)$', 'forum.views.forum'),
    (r'^forum/posting.so$', 'forum.views.reply'),
    (r'^forum/reply.so.(?P<post_id>\d+)$', 'forum.views.reply'),
    (r'^forum/thread-0.so.(?P<post_id>\d+)$', 'forum.views.thread'),
    (r'^forum/thread-(?P<page>\d+).so.(?P<post_id>\d+)$', 'forum.views.thread'),
    (r'^forum/createtopic.so.(?P<forum_id>\d+)$', 'forum.views.topic_create'),
    (r'^forum/createforum.so$', 'forum.views.forum_create'),
    (r'^forum/tagsearch.so/(?P<tag_name>.*)$', 'forum.views.tags_search'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-0.so.(?P<user_id>\d+)$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit-0.so$', 'userauth.views.profile_edit'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    url(r'^blog/librss-0.so.(?P<blog_id>\d+)$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-0.so.(?P<blog_id>\d+)$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
