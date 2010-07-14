from django.contrib import admin
from taverna.blog.models import Blog, Tag

class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'active', 'owner',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

admin.site.register(Blog, BlogAdmin)
admin.site.register(Tag, TagAdmin)


