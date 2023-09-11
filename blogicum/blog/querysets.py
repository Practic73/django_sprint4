from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404

from blog.models import Post, Comment


def filter_posts(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )


def posts():
    return Post.objects.select_related(
        'location',
        'author',
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def posts_filter_full(category_id=None):
    POSTS = filter_posts(posts())

    if category_id:
        return POSTS.filter(category_id=category_id)
    return POSTS


def posts_filter_author(author_id, user):
    POSTS = posts().filter(author_id=author_id)
    post = POSTS.first()

    if post is not None:
        author = post.author
        if author == user:
            return POSTS

    return filter_posts(POSTS)


def get_post(pk, author=None):
    if author:
        return get_object_or_404(Post, pk=pk, author=author)
    return get_object_or_404(Post, pk=pk)


def get_post_filter_author(pk, user):
    post = get_post(pk)
    author = post.author
    posts_filter = filter_posts(Post.objects)
    if user == author:
        return post

    return get_object_or_404(posts_filter, pk=pk)


def comment(id, post_id, user):
    return get_object_or_404(Comment,
                             id=id,
                             post_id=post_id,
                             author=user)
