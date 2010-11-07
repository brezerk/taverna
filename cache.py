from django.core.cache import cache

class CacheManager:
    def clear_template_cache(self, key, *variables):
        from django.utils.http import urlquote
        from django.utils.hashcompat import md5_constructor

        args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
        cache_key = 'template.cache.%s.%s' % (key, args.hexdigest())
        cache.delete(cache_key)

    def clear_cache(self, pattern):
        print cache.get('keys', set())
        for item in cache.get('keys', set()):
            if item.find(pattern) >= 0:
                cache.delete(item)
                self.pop_key(item)

    def request_cache(self, key, default=None, timeout=None):
        if cache.has_key(key):
            print "Key %s mem hit!" % (key)
            return cache.get(key)
        else:
            print "Key %s undefined." % (key)
            if default is not None:
                cache.set(key, default, timeout)
                self.push_key(key)
                return default
        return None

    def push_key(self, key):
        keys = cache.get('keys', set())
        keys.add(key)
        cache.set('keys', keys)

    def pop_key(self, key):
        keys = cache.get('keys', set())
        keys.discard(key)
        cache.set('keys', keys)

