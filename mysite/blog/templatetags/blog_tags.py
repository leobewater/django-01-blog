from django import template
from django.db.models import Count

from ..models import Post

# Create custom template tag

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()
