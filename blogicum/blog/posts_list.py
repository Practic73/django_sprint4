from django.core.paginator import Paginator


NUMBER_POSTS_LIST = 10


def number_posts_list(request, post_list):
    paginator = Paginator(post_list, NUMBER_POSTS_LIST)
    page_number = request.GET.get('page')
    post_list = paginator.get_page(page_number)
    return post_list
