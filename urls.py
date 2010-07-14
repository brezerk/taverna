from django.conf.urls.defaults import *
from django.conf import settings
from django.core.urlresolvers import reverse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from taverna.blog.feeds import RssBlogTraker, AtomBlogTraker, RssBlog, AtomBlog
from taverna.blog.sitemaps import BlogSitemap
from taverna.forum.feeds import RssForum, AtomForum, RssComments, AtomComments

admin.autodiscover()


sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),


    (r'^libthread-0.so.(?P<post_id>\d+)$', 'forum.views.thread'),
    (r'^libthread-(?P<page>\d+).so.(?P<post_id>\d+)$', 'forum.views.thread'),

    (r'^$', 'blog.views.index'),
    (r'^blog/libblog-(?P<page>\d+).so$', 'blog.views.index'),

    (r'^blog/libblog-0.so.(?P<blog_id>\d+)$', 'blog.views.view'),
    (r'^blog/libblog-(?P<page>\d+).so.(?P<blog_id>\d+)$', 'blog.views.view'),

    (r'^blog/all/libblog-0.so.(?P<user_id>\d+)$', 'blog.views.view_all'),
    (r'^blog/all/libblog-(?P<page>\d+).so.(?P<user_id>\d+)$', 'blog.views.view_all'),

    url(r'^librss-0.so$', RssBlogTraker(), name='rss_blog_traker'),
    url(r'^libatom-0.so$', AtomBlogTraker(), name='atom_blog_traker'),
    (r'^blogs/$', 'blog.views.list'),
    (r'^blogs/public/$', 'blog.views.list_public'),
    (r'^blogs/users/$', 'blog.views.list_users'),
    (r'^blog/libpost-new-1.so$', 'blog.views.post_add'),
    (r'^blog/libsettings-0.so$', 'blog.views.settings'),
    (r'^blog/libtag-0.so.(?P<tag_id>\d+)$', 'blog.views.tags_search'),
    (r'^blog/libtag-(?P<page>\d+).so.(?P<tag_id>\d+)$', 'blog.views.tags_search'),

    (r'^forum.so$', 'forum.views.index'),
    (r'^forum-0.so.(?P<forum_id>\d+)$', 'forum.views.forum'),

    url(r'^forum/librss-0.so.(?P<forum_id>\d+)$', RssForum(), name='rss_forum_traker'),
    url(r'^forum/libatom-0.so.(?P<forum_id>\d+)$', AtomForum(), name='atom_forum_traker'),


    (r'^forum-(?P<page>\d+).so.(?P<forum_id>\d+)$', 'forum.views.forum'),
    (r'^forum/posting.so$', 'forum.views.reply'),
    (r'^libreply.so.(?P<post_id>\d+)$', 'forum.views.reply'),

    url(r'^thread/librss-0.so.(?P<post_id>\d+)$', RssComments(), name='rss_comments'),
    url(r'^thread/libatom-0.so.(?P<post_id>\d+)$', AtomComments(), name='atom_comments'),

    (r'^forum/createtopic.so.(?P<forum_id>\d+)$', 'forum.views.topic_create'),
    (r'^forum/createforum.so$', 'forum.views.forum_create'),
    (r'^forum/tagsearch-0.so/(?P<tag_name>.*)$', 'forum.views.tags_search'),
    (r'^forum/tagsearch-(?P<page>\d+).so/(?P<tag_name>.*)$', 'forum.views.tags_search'),

    (r'^liboffset-(?P<root_id>\d+).so.(?P<offset_id>.*)$', 'forum.views.offset'),

    (r'^pam/liblogout.so$', 'userauth.views.openid_logout'),
    (r'^pam/libprofile-0.so.(?P<user_id>\d+)$', 'userauth.views.profile_view'),
    (r'^pam/libprofile-edit-0.so$', 'userauth.views.profile_edit'),

    (r'^pam/libcomments-0.so.(?P<user_id>\d+)$', 'userauth.views.user_comments'),
    (r'^pam/libcomments-(?P<page>\d+).so.(?P<user_id>\d+)$', 'userauth.views.user_comments'),

    (r'^login/$', 'userauth.views.openid_chalange'),
    (r'^login/finish/$', 'userauth.views.openid_finish'),

    url(r'^blog/librss-0.so.(?P<blog_id>\d+)$', RssBlog(), name='rss_blog'),
    url(r'^blog/libatom-0.so.(?P<blog_id>\d+)$', AtomBlog(), name='atom_blog'),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

settings.LOGIN_URL = "/login/"
