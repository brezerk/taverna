from django.core.cache import cache

class CacheManager:
    def clear_template_cache(self, key, *variables):
        from django.utils.http import urlquote
        from django.utils.hashcompat import md5_constructor

        args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
        cache_key = 'template.cache.%s.%s' % (key, args.hexdigest())
        cache.delete(cache_key)
        print "Remove template cache %s" % (cache_key)

    def delete(self, key):
        print "Remove key: %s" % (key)
        cache.delete(key)
        self.pop_key(key)

    def clear_cache(self, pattern):
        print "Removeing keys by pattern: %s" % (pattern)
        for item in cache.get('keys', set()):
            if item.find(pattern) >= 0:
                cache.delete(item)
                self.pop_key(item)
                print " + remove item: %s" % (item)

    def set(self, key, value):
        print "Set key: %s" % (key)
        cache.set(key, value)
        self.push_key(key)

    def get(self, key):
        print "Get key %s" % (key)
        return cache.get(key)

    def request_cache(self, key, default=None, timeout=None):
        ret = cache.get(key)

        if ret is not None:
            print "Key %s mem hit!" % (key)
        else:
            print "Key %s undefined." % (key)
            if default is not None:
                cache.set(key, default, timeout)
                self.push_key(key)
                return default
        return ret

    def push_key(self, key):
        keys = cache.get('keys', set())
        keys.add(key)
        cache.set('keys', keys)

    def pop_key(self, key):
        keys = cache.get('keys', set())
        keys.discard(key)
        cache.set('keys', keys)

