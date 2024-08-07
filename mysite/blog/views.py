from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post


# Search
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Search in title and body columns using SearchVector with stop words based on defined language
            # search_vector = SearchVector('title', 'body', config='spanish')

            """
            In the preceding code, we apply different weights to the search vectors built using the title and body fields. The default weights are D, C, B, and A, and they refer to the numbers 0.1, 0.2, 0.4, and 1.0, respectively. We apply a weight of 1.0 to the title search vector (A) and a weight of 0.4 to the body vector (B). Title matches will prevail over body content matches. We filter the results to display only the ones with a rank higher than 0.3.
            """
            search_vector = SearchVector(
                'title', weight='A') + SearchVector('body', weight='B')

            # SearchQuery removes any stop words such as "a", "an", "of"...
            '''
            https://github.com/postgres/postgres/blob/master/src/backend/snowball/stopwords/spanish.stop
            '''
            # search_query = SearchQuery(query, config='spanish')
            search_query = SearchQuery(query)

            # Use SearchRank, ranking by number of occurrences of the search term
            results = (Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            )
                # .filter(search=query)
                # .filter(rank__gte=0.3)
                .filter(similarity__gt=0.1)
                .order_by('-rank')
            )

    return render(request, 'blog/post/search.html', {
        'form': form,
        'query': query,
        'results': results
    })


# Accept POST only otherwise throw 405 error
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    # A comment was posted
    form = CommentForm(data=request.POST)

    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {
        'post': post,
        'form': form,
        'comment': comment
    })


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) " f"recommends you read {post.title}")
            message = (f"Read {post.title} at {post_url}\n\n" f"{
                       cd['name']}\s comments: {cd['comments']}")

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent
    })


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# Function-base views
# Accept optional tag_slug parameter
def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    # Filter Tag
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not int, show first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range, show the last page
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'tag': tag
    })


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             )

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    # Form for users to comment
    form = CommentForm()

    # List of similar posts (related posts)
    post_tags_ids = post.tags.values_list('id', flat=True)
    # Get all similar tags posts but exclude itself
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    # use Count aggregation function to generate a calculated field "same_tags"
    similar_posts = similar_posts.annotate(same_tags=Count(
        'tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
    })
