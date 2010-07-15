from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.forum.models import Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from taverna.parsers.templatetags.markup import markup

from django.core.paginator import Paginator

from django.conf import settings

class RssUser(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, user_id):
        return get_object_or_404(User, pk=user_id)

    def items(self, obj):
        self.title =  _("Last %s topics of user \"%s\"" % (settings.PAGE_LIMITATIONS["BLOG_POSTS"], obj.profile.get_visible_name()))
        self.link = obj.get_absolute_url()
        return Post.objects.exclude(forum=None,blog=None).filter(owner=obj).order_by('-created')[:settings.PAGE_LIMITATIONS["BLOG_POSTS"]]

    def item_title(self, item):
        if (item.forum):
            return "%s - %s" % (item.forum.name, item.title)
        else:
            return "%s - %s" % (item.blog.name, item.title)

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomUser(RssUser):
    feed_type = Atom1Feed

