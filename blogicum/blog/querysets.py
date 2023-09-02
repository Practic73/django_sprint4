from django.utils import timezone
from django.db.models import Count

from blog.models import Post


def time_now():
    return timezone.now()


POST_QS = Post.objects.select_related(
    'location', 'author').order_by('-pub_date')

POST_QS_FILTER = POST_QS.filter(is_published=True,
                                category__is_published=True,
                                pub_date__lte=time_now())

POST_QS_COMM_COUNT = POST_QS_FILTER.annotate(comment_count=Count('comments'))


def post_qs_filter_author(author):
    return POST_QS.filter(author=author).annotate(
        comment_count=Count('comments'))


def post_qs_filter_full(author):
    return POST_QS_COMM_COUNT.filter(author=author)
