from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/create/', views.post_create, name='create_post'),
    path(
        'posts/<post_id>/edit/',
        views.post_edit,
        name='edit_post'
    ),
    path(
        'posts/<post_id>/delete/',
        views.post_delete,
        name='delete_post'
    ),
    path(
        'posts/<int:pk>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/<username>/',
        views.profile,
        name='profile'
    ),
    path(
        'profile/<username>/edit/',
        views.profile_edit,
        name='edit_profile'
    ),
    path(
        'posts/<post_id>/comment/',
        views.comment_create,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.comment_edit,
        name='edit_comment'
    ),
    path(
        'posts/<post_id>/delete_comment/<comment_id>/',
        views.comment_delete,
        name='delete_comment'
    ),
]
