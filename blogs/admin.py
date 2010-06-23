from django.contrib import admin
from taverna.blogs.models import Blog, Post, Tag

class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'active', 'owner',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'blog', 'created')

admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)


