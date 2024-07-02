from django.contrib import admin

from .models import Post

# admin.site.register(Post)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    # auto generate slug with title
    prepopulated_fields = {'slug': ('title',)}
    # show id instead of name for author, better when have tons of users
    raw_id_fields = ['author']
    # show a row of date selection
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    # show facet filters counts
    show_facets = admin.ShowFacets.ALWAYS
