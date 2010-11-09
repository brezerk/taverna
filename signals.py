from cache import CacheManager

def drop_post_cache(instance):
    manager = CacheManager()

    print instance.blog
    print instance.forum
    print instance.thread

    if instance.blog is not None:
        manager.clear_template_cache("post_main", instance.pk)
        manager.clear_template_cache("post_free", instance.pk)
        manager.clear_template_cache("startpost_main", instance.pk)
        manager.clear_template_cache("startpost_free", instance.pk)
        manager.clear_cache("posts.blog.all")
        manager.clear_cache("posts.blog.%s" % (instance.blog.pk))
        manager.delete("posts.%s" % (instance.pk))
    elif instance.forum is not None:
        pass
    elif instance.thread is not None:
        manager.clear_cache("posts.%s.comments" % instance.thread.pk)

