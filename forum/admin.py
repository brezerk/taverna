from django.contrib import admin
from taverna.forum.models import Forum, Post

class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner', 'rating')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

admin.site.register(Forum, ForumAdmin)
admin.site.register(Post, PostAdmin)


