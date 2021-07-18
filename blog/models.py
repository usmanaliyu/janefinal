from django.db import models
from django.conf import settings
# Create your models here.

BLOG_TAGS = (
    ('FASHION', "FASHION"),
    ('LIFESTYLE', "LIFESTYLE"),
    ('TRAVEL', "TRAVEL"),
)


class Blog(models.Model):
    author = models.ForeignKey(
        "core.Author", on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100)
    featured = models.BooleanField(default=False)
    intro = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    tags = models.CharField(max_length=100, choices=BLOG_TAGS)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def get_comment_count(self):
        return self.blogcomment_set.all().count()

    @property
    def get_comment(self):
        return self.blogcomment_set.all()

    class Meta:
        unique_together = ['title', 'slug']


class BlogComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(
        Blog, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
