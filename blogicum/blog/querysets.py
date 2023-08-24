from django.utils import timezone
from django.db.models import Count
from blog.models import Post


def post_queryset():
    queryset = Post.objects.select_related(
        'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    return queryset