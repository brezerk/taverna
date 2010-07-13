from django.contrib.syndication.views import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from taverna.forum.models import Forum, Post
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taverna.parsers.templatetags.markup import markup

class RssForum(Feed):
    link = ""
    description = ""
    title = ""

    def get_object(self, request, forum_id):
        return get_object_or_404(Forum, pk=forum_id)

    def items(self, obj):
        self.title =  _("Last 30 topics in \"%s\" forum" % (obj.name))
        self.description = obj.description
        self.link = obj.get_absolute_url()
        return Post.objects.filter(forum=obj, reply_to = None).order_by('-created')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markup(item.text, item.parser)

class AtomForum(RssForum):
    feed_type = Atom1Feed
    subtitle = RssForum.description
