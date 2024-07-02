from django import template
from django.db.models import Count

from ..models import Post

# Create custom template tag

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


# Note that the function returns a dictionary of variables instead of a simple value. Inclusion tags have to return a dictionary of values, which is used as the context to render the specified template.
# {% show_latest_posts 3 %}
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
