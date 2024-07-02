from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Custom model manager to filter published posts
class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )


class Post(models.Model):
    # Enum class
    class Status(models.TextChoices):
        # name = value, label
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)

    # add unique key with slug and publish columns
    slug = models.SlugField(max_length=250, unique_for_date='publish')

    # many-to-one relationship
    # related_name to specify the name of the reverse relationship, from User to Post such as user.blog_posts
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts")
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # auto_now_add - time will be saved when created
    created = models.DateTimeField(auto_now_add=True)
    # auto_now update automatically when save
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status, default=Status.DRAFT)

    # The default model manager
    objects = models.Manager()
    # Use our custom manager
    published = PublishedManager()

    class Meta:
        # default sort results in publish DESC order
        ordering = ['-publish']

        # add index to publish col in -publish Desc order
        # Index ordering is not supported on MySQL. If you use MySQL for the database, a descending index will be created as a normal index.
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title

    # use Canonical URL
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug,
        ])
