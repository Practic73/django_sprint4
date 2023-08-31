from typing import Any, Optional
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views import generic

from blog.models import Post, Category, Comment
from blog.forms import PostForm, UserUpdateForm, CommentForm
from blog.querysets import (POST_QS_FILTER,
                            POST_QS,
                            time_now,
                            post_qs_filter_author,
                            post_qs_filter_full)
from blog import mixins

PAGINATOR = 10


class IndexView(generic.ListView):
    paginate_by = PAGINATOR
    template_name = 'blog/index.html'
    queryset = POST_QS_FILTER


class CategoryPostsView(IndexView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        return POST_QS_FILTER.filter(
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
        if self.request.user.is_authenticated and self.request.user == author:
            object_list = post_qs_filter_author(author)
        else:
            object_list = post_qs_filter_full(author)

        context = super().get_context_data(**kwargs)
        page_num = self.request.GET.get('page')
        paginator = Paginator(object_list, PAGINATOR)
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


class PostCreateView(mixins.PostFormMixin,
                     mixins.SuccessUrlProfileMixin,
                     generic.CreateView
                     ):
    pass


class PostUpdateView(mixins.AuthorMixin,
                     mixins.PostFormMixin,
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
            object = get_object_or_404(POST_QS_FILTER)

        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        #context['comments'] = Comment.objects.filter(post_id=self.object.id) comments
        context['comments'] = Comment.objects.filter(post_id=self.object.id)
        return context


class PostDeleteView(LoginRequiredMixin,
                     mixins.AuthorMixin,
                     mixins.PostMixin,
                     generic.DeleteView
                     ):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            self.request.POST or None,
            instance=context['post']
        )
        return context


class CommentCreateView(generic.detail.SingleObjectMixin,
                        mixins.CommentMixin,
                        generic.FormView
                        ):
    model = Post
    form_class = CommentForm
    template_name = 'blog/add_comment.html'
    pk_url_kwarg = 'post_id'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)


class CommentUpdateView(mixins.CommentDispathMixin,
                        generic.UpdateView
                        ):
    form_class = CommentForm


class CommentDeleteView(mixins.CommentDispathMixin,
                        generic.DeleteView
                        ):
    pass
