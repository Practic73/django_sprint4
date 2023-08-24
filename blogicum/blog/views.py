
from typing import Any, Dict
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from blog.models import Post, Category, Comment
from blog.forms import PostForm, UserUpdateForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .querysets import post_queryset

INT_PAGINATOR = 10


class IndexView(ListView):
    ordering = ('-pub_date',)
    paginate_by = INT_PAGINATOR
    template_name = 'blog/index.html'

    # queryset = Post.objects.select_related(
    #     'location', 'author'
    # ).filter(
    #     is_published=True,
    #     category__is_published=True,
    #     pub_date__lte=timezone.now(),
    # ).annotate(comment_count=Count('comments'))
    queryset = post_queryset()
    

class CategoryPostsView(IndexView):
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        obj = post_queryset().filter(category__slug=self.kwargs['category_slug'])
        return obj
    #queryset = post_queryset()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        context['category'] = category

        return context
    


    # def get_queryset(self):
    #     category = get_object_or_404(
    #         Category,
    #         slug=self.kwargs['category_slug'],
    #         is_published=True
    #     )
    #     return super().get_queryset().filter(category_id=category.id)


class ProfileView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        author = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user.is_authenticated and self.request.user == author:
            object_list = (
                Post.objects.select_related(
                     'location', 'author'
                ).filter(author=author).
                order_by('-pub_date').
                annotate(comment_count=Count('comments'))
            )
        else:
            object_list = (
                Post.objects.select_related(
                     'location', 'author'
                ).filter(author=author, pub_date__lte=timezone.now()).
                order_by('-pub_date').
                annotate(comment_count=Count('comments'))
            )
        context = super().get_context_data(**kwargs)
        page_num = self.request.GET.get('page')
        paginator = Paginator(object_list, INT_PAGINATOR)
        context['page_obj'] = paginator.get_page(page_num)
        context['object'] = author
        return context


class SuccessUrlProfileMixin:

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class SuccessUrlDeteileMixin:

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class ProfileUpdateView(LoginRequiredMixin,
                        ProfileView,
                        SuccessUrlProfileMixin,
                        UpdateView
                        ):

    form_class = UserUpdateForm
    template_name = 'blog/user.html'


class PostMixin:

    model = Post
    template_name = 'blog/create.html'


class PostFormMixin(PostMixin):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin,
                     PostFormMixin,
                     SuccessUrlProfileMixin,
                     CreateView
                     ):
    pass


class PostUpdateView(PostFormMixin, SuccessUrlDeteileMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if (
            not self.request.user.is_authenticated
            or instance.author != request.user
        ):
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post=context['post']
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            if (
                not instance.is_published
                or not instance.category.is_published
                or instance.pub_date > timezone.now()
            ):
                raise Http404()
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            self.request.POST or None,
            instance=context['post']
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentMixin(SuccessUrlDeteileMixin):
    model = Comment
    template_name = 'blog/comment.html'


class CommentDispathMixin(CommentMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    post_ = None
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_ = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.post_
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentDispathMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentDispathMixin, DeleteView):
    pass
