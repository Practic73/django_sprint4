from django.shortcuts import redirect


def redirect_post(pk):
    return redirect('blog:post_detail', pk=pk)


def redirect_profil(username):
    return redirect('blog:profile', username=username)
