import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

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


# Create a simple template tag that returns a value. We will store the result in a variable that can be reused, rather than outputting it directly. We will create a tag to display the most commented posts.
@register.simple_tag
def get_most_commented_posts(count=5):
    # build a QuerySet using the annotate() function to aggregate the total number of comments for each post.
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


# Custom filter {{ variable|markdown }}
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
