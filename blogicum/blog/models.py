from django.db import models
from blog.abstracts import BaseModel, BaseTitleModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Location(BaseModel):

    name = models.CharField(
        'Название места',
        max_length=256,
    )

    class Meta:
        verbose_name = ('местоположение')
        verbose_name_plural = ('Местоположения')

    def __str__(self):
        return self.name


class Category(BaseTitleModel):

    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = ('категория')
        verbose_name_plural = ('Категории')


class Post(BaseTitleModel):

    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='location',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category',
        verbose_name='Категория',
    )
    image = models.ImageField('Foto', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = ('публикация')
        verbose_name_plural = ('Публикации')
        ordering = ('-pub_date',)


class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    class Meta:
        default_related_name = ('comments')
        ordering = ('created_at',)
