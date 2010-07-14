from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.blog.models import Blog
from taverna.forum.models import Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taverna.parsers.templatetags.markup import markup

from django.core.paginator import Paginator

class RssBlogTraker(Feed):
    title = _("Last 10 blogs topics")
    link = "/"
    description = _("Updates on changes and additions to blogs topics.")

    def items(self):
        return Post.objects.exclude(blog = None).order_by('-created')[:10]

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomBlogTraker(RssBlogTraker):
   feed_type = Atom1Feed
   subtitle = RssBlogTraker.description

class RssBlog(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, blog_id):
        return get_object_or_404(Blog, pk=blog_id)

    def items(self, obj):
        self.title =  _("Last 10 topics for \"%s\" blog" % (obj.name))
        self.description = obj.desc
        self.link = obj.get_absolute_url()
        return Post.objects.filter(blog=obj).order_by('-created')[:10]

    def item_title(self, item):
        return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomBlog(RssBlog):
    feed_type = Atom1Feed
    subtitle = RssBlog.description

