from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post
from yatube.settings import LENGTH_POST

User = get_user_model()


class PostModelTest(TestCase):
    """
    Устанавливаем данные для тестирования posts/models.
    """

    @classmethod
    def setUpClass(cls):
        """
        Создаём тестовую запись в БД
        и сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)

    def test_models_first_15_symbols(self):
        """Проверяем, первые 15 символов выводимые в __str__."""
        self.assertEqual(str(self.post)[:LENGTH_POST], self.post.text)
