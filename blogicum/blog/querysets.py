from django.utils import timezone
from django.db.models import Count

from blog.models import Post


def time_now():
    return timezone.now()


POST_QS = Post.objects.select_related('location', 'author').annotate(
    comment_count=Count('comments')).order_by('-pub_date')

POST_QS_FILTER = POST_QS.filter(is_published=True,
                                category__is_published=True,
                                pub_date__lte=time_now())


def post_qs_filter_author(author):
    return POST_QS.filter(author=author)


def post_qs_filter_full(author):
    return POST_QS_FILTER.filter(author=author)
