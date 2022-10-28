from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    """
    Устанавливаем данные для тестирования posts/forms.
    """

    @classmethod
    def setUpClass(cls: TestCase):
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
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        """
        Создаём различные экземпляры клиента.
        Для проверки работоспобоности программы при
        разных уровнях авторизации.
        """
        self.guest_client = Client()
        self.user = PostFormTests.user
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.user_not_author = User.objects.create(username='not_author')
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_post_create_form(self):
        """Проверяем создание и редактирование поста с отправлением формы."""

        # Константа для проверки был ли создан новый пост.
        MORE_POST: int = 1

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + MORE_POST)
