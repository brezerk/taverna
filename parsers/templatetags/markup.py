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
    value = value.replace("---cut---", "<hr>")
    value = value.replace("&mdash;cut&mdash;", "<hr>")
    return value

@register.filter
@stringfilter
def strip_cut(value):
    value = value.replace("---cut---", "")
    value = value.replace("&mdash;cut&mdash;", "")
    return value

@register.filter
@stringfilter
def markup(value, parser):
    esc = conditional_escape
    if parser == 1:
        import postmarkup
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, ClassNotFound
        #from pygments.lexers import guess_lexer
        from pygments.formatters import HtmlFormatter


        markup = postmarkup.create(annotate_links=False,exclude=["img", "code"],use_pygments=False)

        class ImgTag(postmarkup.TagBase):
            valid_params = ("left", "right")

            def __init__(self, name, **kwargs):
                postmarkup.TagBase.__init__(self, name, inline=True)

            def render_open(self, parser, node_index):
                contents = self.get_contents(parser)
                self.skip_contents(parser)
                contents = postmarkup.strip_bbcode(contents).replace(u'"', "%22")

                if self.params in self.valid_params:
                    return u'<img class="float-%s" src="%s" alt="%s">' % (self.params, contents, contents)
                else:
                    return u'<img src="%s" alt="%s">' % (contents, contents)

        class PygmentsCodeTag(postmarkup.TagBase):
            def __init__(self, name, pygments_line_numbers=True, **kwargs):
                postmarkup.TagBase.__init__(self, name, enclosed=True, strip_first_newline=True)
                self.line_numbers = pygments_line_numbers

            def render_open(self, parser, node_index):
                contents = self.get_contents(parser)
                self.skip_contents(parser)

                #if self.params:
                try:
                    lexer = get_lexer_by_name(self.params, stripall=True)
                except ClassNotFound:
                    contents = postmarkup._escape_no_breaks(contents)
                    return '<div class="code"><pre>%s</pre></div>' % contents
                #Well, do we realy need lexer gues?
                #else:
                #    lexer = guess_lexer(contents)

                formatter = HtmlFormatter(linenos='inline', cssclass="code")
                return highlight(contents, lexer, formatter)

        markup.add_tag(ImgTag, u'img')
        markup.add_tag(PygmentsCodeTag, u'code')
        markup.add_tag(postmarkup.SimpleTag, u'block', u'div class="mblock"')

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
    elif parser == 4:
        from django.template.defaultfilters import removetags
        value = removetags(value, 'style html script applet form frame iframe map noframes noscript object var area input button select')
        value = linebreaks(value)
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
    if len(list) <= 1:
        list = value.split("&mdash;cut&mdash;")

    if len(list) > 1:
        value = markup(list[0], post.parser)
        value = value + "<div class='block'>&gt;&gt;&gt; <a href='%s'>%s</a></div>" % (reverse('forum.views.thread', args=[post.pk]), _("Read full post"))
    else:
        value = markup(value, post.parser)
    return value

@register.filter
def pg(value, paginator):
    for page in paginator.page_range:
        if value in paginator.page(page).object_list:
            return page
    return 0;

