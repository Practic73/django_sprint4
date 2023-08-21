from django.db import models


class BaseModel(models.Model):

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class BaseTitleModel(BaseModel):

    title = models.CharField(
        'Заголовок',
        max_length=256,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
