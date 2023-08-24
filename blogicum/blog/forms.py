from django import forms


from .models import Post, User, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published',)
        widgets = {'pub_date': forms.DateTimeInput(attrs={'type': 'date'})}


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
