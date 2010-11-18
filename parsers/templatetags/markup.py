# -*- coding: utf-8 -*-

# Copyright (C) 2010 by Alexey S. Malakhov <brezerk@gmail.com>
#                       Opium <opium@jabber.com.ua>
#
# This file is part of Taverna
#
# Taverna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taverna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Taverna.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from django.utils.html import linebreaks
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape, urlize

from django.template.defaultfilters import removetags

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import re

register = template.Library()

@register.filter
@stringfilter
def show_cut(value):
    return value.replace("---cut---", "<div class='cut'>&nbsp;</div>")

@register.filter
@stringfilter
def strip_cut(value):
    value = value.replace("---cut---", "")
    return value

@register.filter
@stringfilter
def markup(value, parser):
    esc = conditional_escape
    if parser == 1:
        import postmarkup
        markup = postmarkup.create(annotate_links=False,exclude=["img"],use_pygments=False)

        class ImgTag(postmarkup.TagBase):
            valid_params = ("left", "right")

            def __init__(self, name, **kwargs):
                postmarkup.TagBase.__init__(self, name, inline=True)

            def render_open(self, parser, node_index):
                contents = self.get_contents(parser)
                self.skip_contents(parser)
                contents = postmarkup.strip_bbcode(contents).replace(u'"', "%22")

                if self.params in self.valid_params:
                    return u'<img class="float-%s" src="%s" alt="%s"></img>' % (self.params, contents, contents)
                else:
                    return u'<img src="%s" alt="%s"></img>' % (contents, contents)

        markup.add_tag(ImgTag, u'img')

        value = "<p>" + markup(value) + "</p>"
        return value
    elif parser == 2:
        from markdown import markdown
        value = esc(value)
        value = markdown(value)
        return value
    elif parser == 3:
        from wikimarkup import parselite
        value = parselite(value)
    else:
        value = esc(value)
        value = urlize(value)
        value = linebreaks(value)
    return value

@register.filter
@stringfilter
def tags(value):
    tag_list = value.split(", ")
    value = ""

    first = True

    for tag in tag_list:
        if first:
            first = False
        else:
            value = value + ", "
        value = value + "<a href='/'>" + tag + "</a>"
    return value

#@register.filter
#def forumtags(value):
#    tag_list = re.split('\[(.*?)\]', value.title)
#    tag_string = ""
#
#    for tag in tag_list:
#        if tag:
#           if tag != tag_list[-1]:
#               tag_string = tag_string + u"[<a href='/forum/tagsearch.so/%s'>%s</a>]" % (tag, tag)
#
#    tag_string = tag_string + u"<a href='%s'>%s</a>" % (reverse('forum.views.thread', args=[value.pk]), tag_list[-1])
#    return tag_string

@register.filter
def strippost(value, post):
    list = value.split("---cut---")

    if len(list) > 1:
        value = markup(list[0], post.parser)
        value = value + "<div class='more'>>>> <a href='%s'>%s</a></div>" % (reverse('forum.views.thread', args=[post.pk]), _("Read full post"))
    else:
        value = markup(value, post.parser)
    return value

@register.filter
def pg(value, paginator):
    for page in paginator.page_range:
        if value in paginator.page(page).object_list:
            return page
    return 0;

