from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic

from blog.models import Post, Comment
from blog.forms import PostForm
from blog.querysets import POST_QS_COMM_COUNT

PAGINATOR = 10


class SuccessUrlProfileMixin:

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class SuccessUrlDetaileMixin:

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class IndexMixin(generic.ListView):

    paginate_by = PAGINATOR
    queryset = POST_QS_COMM_COUNT


class PostMixin:

    model = Post
    template_name = 'blog/create.html'


class PostFormMixin(LoginRequiredMixin, PostMixin):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentMixin(LoginRequiredMixin, SuccessUrlDetaileMixin):
    model = Comment
    template_name = 'blog/comment.html'


class AuthorMixin(UserPassesTestMixin):
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        if object.author != self.request.user:
            return False
        return True

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs.get(self.pk_url_kwarg)
        )


# Dispath переделан в test_func название осталось старое
class CommentDispathMixin(AuthorMixin, CommentMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
