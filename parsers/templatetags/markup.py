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
from postmarkup import render_bbcode
import markdown
import string
import re

from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

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

    if parser == 1:
        value = "<p>" + render_bbcode(value) + "</p>"
        return value
    elif parser == 2:
        value = markdown.markdown(value)
        return value
    else:
        esc = conditional_escape
        value = esc(value)
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

@register.filter
def forumtags(value):
    tag_list = re.split('\[(.*?)\]', value.title)
    tag_string = ""

    for tag in tag_list:
        if tag:
           if tag != tag_list[-1]:
               tag_string = tag_string + u"[<a href='/forum/tagsearch.so/%s'>%s</a>]" % (tag, tag)

    tag_string = tag_string + u"<a href='%s'>%s</a>" % (reverse('forum.views.thread', args=[value.pk]), tag_list[-1])
    return tag_string

@register.filter
def strippost(value, post):

    list = value.split("---cut---")

    if len(list) > 1:
        value = markup(list[0], post.parser)
        value = value + "<br>>>> <a href='%s'>%s</a>" % (reverse('forum.views.thread', args=[post.pk]), _("Read full post"))
    else:
        value = markup(value, post.parser)
    return value

@register.filter
def pg(value, paginator):
    for page in paginator.page_range:
        if value in paginator.page(page).object_list:
            return page

    return 0;

