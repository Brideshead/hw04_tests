from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()

class PostFormTests(TestCase):
    """"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

        cls.form = PostForm()


    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = PostFormTests.user
        # Создаем второй клиент
        self.authorized_client_author = Client()
        # Авторизуем пользователя
        self.authorized_client_author.force_login(self.user)
        self.user_not_author = User.objects.create(username='not_author')
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author) 

    def test_post_create_form(self):
        """Posts.Forms. Создание нового Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostFormTests.group.pk
        }

        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    