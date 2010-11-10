from cache import CacheManager

def drop_post_cache(instance):
    manager = CacheManager()

    if instance.blog is not None:
        manager.clear_template_cache("post_main", instance.pk)
        manager.clear_template_cache("post_free", instance.pk)
        manager.clear_template_cache("startpost_main", instance.pk)
        manager.clear_template_cache("startpost_free", instance.pk)
        manager.clear_cache("posts.blog.all")
        manager.clear_cache("posts.blog.%s" % (instance.blog.pk))
        manager.delete("posts.%s" % (instance.pk))
    elif instance.forum is not None:
        manager.clear_template_cache("forum_item", instance.pk)
        manager.clear_template_cache("post_main", instance.pk)
        manager.clear_template_cache("post_free", instance.pk)
        manager.clear_template_cache("startpost_main", instance.pk)
        manager.clear_template_cache("startpost_free", instance.pk)
        manager.clear_cache("posts.forum.%s" % (instance.forum.pk))
        manager.delete("posts.%s" % (instance.pk))
    elif instance.thread is not None:
        manager.clear_cache("posts.%s.comments" % instance.thread.pk)

def drop_postedit_cache(instance):
    manager = CacheManager()
    manager.clear_cache("postedit.%s.all" % instance.pk)

def drop_post_tag_cache(name):
    manager = CacheManager()

    from taverna.blog.models import Tag
    tag = Tag.objects.get(name = name)
    manager.clear_cache("posts.blog.tag.%s" % tag.pk)

