from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404

from blog.models import Post, Comment


def posts():
    return Post.objects.select_related(
        'location',
        'author',
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def posts_filter_full(category_id=None):
    POSTS = posts().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )
    if category_id:
        return POSTS.filter(category_id=category_id)
    return POSTS


def posts_filter_author(author_id):
    POSTS = posts().filter(author_id=author_id)
    return POSTS


def post(pk, author=None):
    if author:
        return get_object_or_404(Post, pk=pk, author=author)
    return get_object_or_404(Post, pk=pk)


def post_filter_author(pk, user):
    author = post(pk).author

    if user == author:
        return post(pk)

    return get_object_or_404(Post, pk=pk,
                             is_published=True,
                             category__is_published=True,
                             pub_date__lte=timezone.now())


def comment(id, post_id, user):
    return get_object_or_404(Comment,
                             id=id,
                             post_id=post_id,
                             author=user)
