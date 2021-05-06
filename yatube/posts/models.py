from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="posts", verbose_name="Автор"
    )
    group = models.ForeignKey(
        "Group", on_delete=models.SET_NULL, related_name="posts",
        blank=True, null=True, verbose_name="Группа"
    )
    image = models.ImageField(
        upload_to="posts/", blank=True,
        null=True, verbose_name="Изображение"
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Пост комментария"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор комментария"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-created"]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower", verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following", verbose_name="Автор подписки"
    )

    class Meta:
        unique_together = ["user", "author"]
