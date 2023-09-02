from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from blog.models import Post, Category
from blog.forms import PostForm, UserUpdateForm, CommentForm
from blog.querysets import (POST_QS_FILTER, post_qs_filter_author)
from blog import mixins


class IndexView(mixins.IndexMixin):
    template_name = 'blog/index.html'


class CategoryPostsView(mixins.IndexMixin):
    template_name = 'blog/category.html'

    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        context['category'] = category
        return context


class ProfileView(generic.DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        author = self.get_object()
        # Flag is_authenticated and author
        flag = True
        if (not self.request.user.is_authenticated and
                self.request.user != author):
            flag = False

        object_list = post_qs_filter_author(flag, author=author)
        context = super().get_context_data(**kwargs)
        page_num = self.request.GET.get('page')
        paginator = Paginator(object_list, mixins.PAGINATOR)
        context['page_obj'] = paginator.get_page(page_num)
        return context


class ProfileUpdateView(LoginRequiredMixin,
                        mixins.SuccessUrlProfileMixin,
                        generic.UpdateView
                        ):
    model = User
    form_class = UserUpdateForm
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/user.html'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            username=self.request.user
        )


class PostCreateView(mixins.PostFormMixin,
                     mixins.SuccessUrlProfileMixin,
                     generic.CreateView
                     ):
    pass


class PostUpdateView(mixins.AuthorMixin,
                     mixins.PostMixin,
                     mixins.SuccessUrlDetaileMixin,
                     generic.UpdateView
                     ):
    pk_url_kwarg = 'post_id'


class PostDetailView(mixins.PostMixin,
                     generic.DetailView
                     ):
    template_name = 'blog/detail.html'

    def get_object(self):
        object = super().get_object()
        if (object.author != self.request.user):
            object = get_object_or_404(POST_QS_FILTER, pk=self.kwargs['pk'])
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all
        return context


class PostDeleteView(LoginRequiredMixin,
                     mixins.AuthorMixin,
                     mixins.PostMixin,
                     generic.DeleteView
                     ):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(self.request.POST or None,
                                   instance=context['post'])
        return context


class CommentCreateView(mixins.CommentMixin,
                        generic.CreateView
                        ):
    model = Post
    template_name = 'blog/add_comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = get_object_or_404(POST_QS_FILTER,
                                         pk=self.kwargs['post_id'])
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)


class CommentUpdateView(mixins.CommentIdMixin,
                        generic.UpdateView
                        ):
    pass


class CommentDeleteView(mixins.CommentIdMixin,
                        generic.DeleteView
                        ):
    pass
