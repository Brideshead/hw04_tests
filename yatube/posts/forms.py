from django import forms

from posts.models import Post


class PostForm(forms.ModelForm):
    """
    Создание объекта, который передается в качестве
    переменной form в контекст шаблона templates/create_post.html
    """
    class Meta:
        model = Post
        fields = ('text', 'group')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
