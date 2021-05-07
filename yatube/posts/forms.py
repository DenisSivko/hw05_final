from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].empty_label = "Группа не выбрана"

    class Meta:
        model = Post
        fields = ("group", "text", "image")
        labels = {
            "group": "Группа",
            "text": "Текст",
            "image": "Изображение",
        }
        help_texts = {
            "group": "Вы можете выбрать группу, "
            "к которой будет относиться это сообщение.",
            "text": "Обязательное поле.",
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)
