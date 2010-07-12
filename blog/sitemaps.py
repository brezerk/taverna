from django.contrib.sitemaps import Sitemap
from taverna.blog.models import Post

class BlogSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def items(self):
        return Post.objects.order_by('-created')[:10]

    def lastmod(self, obj):
        return obj.created

