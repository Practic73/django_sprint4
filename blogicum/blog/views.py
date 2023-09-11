from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from blog.models import Category, Comment
from blog.posts_list import number_posts_list
from blog.forms import PostForm, UserUpdateForm, CommentForm
from blog.redirects import redirect_profile, redirect_post
from blog.querysets import (posts_filter_full,
                            posts_filter_author,
                            get_post_filter_author,
                            get_post, comment)


def index(request):
    post_list = posts_filter_full()

    post_list = number_posts_list(request, post_list)
    context = {'page_obj': post_list}
    template_name = 'blog/index.html'
    return render(request, template_name, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = posts_filter_full(category.id)

    post_list = number_posts_list(request, post_list)
    template = 'blog/category.html'
    context = {'category': category, 'page_obj': post_list}
    return render(request, template, context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = posts_filter_author(profile.id, request.user)

    post_list = number_posts_list(request, post_list)
    context = {'profile': profile, 'page_obj': post_list}
    template_name = 'blog/profile.html'
    return render(request, template_name, context)


@login_required
def profile_edit(request, username):

    form = UserUpdateForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect_profile(username)

    context = {'form': form}
    template_name = 'blog/user.html'
    return render(request, template_name, context)


def post_detail(request, pk):

    post = get_post_filter_author(pk, request.user)

    comments = Comment.objects.select_related(
        'author'
    ).filter(
        post=post,
    )

    form = CommentForm()

    context = {'post': post, 'form': form, 'comments': comments}
    template_name = 'blog/detail.html'
    return render(request, template_name, context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect_profile(request.user.username)

    context = {'form': form}
    template_name = 'blog/create.html'
    return render(request, template_name, context)


@login_required
def post_edit(request, post_id):

    instance = get_post(post_id)

    if instance.author != request.user:
        return redirect_post(post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)

    if form.is_valid():
        form.save()
        return redirect_post(instance.pk)

    context = {'form': form}
    template_name = 'blog/create.html'
    return render(request, template_name, context)


@login_required
def post_delete(request, post_id):

    instance = get_post(post_id, request.user)
    form = PostForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        instance.delete()
        return redirect_profile(request.user.username)

    context = {'form': form}
    template_name = 'blog/create.html'
    return render(request, template_name, context)


@login_required
def comment_create(request, post_id):

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_post(post_id)
        comment.save()
        return redirect_post(post_id)

    template_name = 'blog/comment.html'
    context = {'form': form}
    return render(request, template_name, context)


@login_required
def comment_edit(request, post_id, comment_id):

    instance = comment(comment_id, post_id, request.user)

    form = CommentForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()
        return redirect_post(post_id)

    context = {'form': form, 'comment': instance}
    template_name = 'blog/comment.html'
    return render(request, template_name, context)


@login_required
def comment_delete(request, post_id, comment_id):
    instance = comment(comment_id, post_id, request.user)

    if request.method == 'POST':
        instance.delete()
        return redirect_post(post_id)

    context = {'comment': instance}
    template_name = 'blog/comment.html'
    return render(request, template_name, context)
