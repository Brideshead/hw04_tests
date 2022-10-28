from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

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
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, PostModelTest.group.title)

    def test_models_first_15_symbols(self):
        """Проверяем, первые 15 символов выводимые в __str__."""

        LENGTH_POST = 15

        post = PostModelTest.post
        expected_object_name = post.text[:LENGTH_POST]
        self.assertEqual(expected_object_name, PostModelTest.post.text)
