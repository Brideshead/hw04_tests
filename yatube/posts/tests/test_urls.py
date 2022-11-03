from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """
    Устанавливаем данные для тестирования posts/urls.
    """

    @classmethod
    def setUpClass(cls):
        """
        Создаём тестовую записи в БД
        и сохраняем созданную запись в качестве переменной класса.
        """
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = mixer.blend(Group)
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.anon = Client()
        cls.client = Client()
        cls.group_list_url = f'/group/{cls.group.slug}/'
        cls.post_edit_url = f'/posts/{cls.post.pk}/edit/'
        cls.post_url = f'/posts/{cls.post.pk}/'
        cls.profile_url = f'/profile/{cls.user.username}/'
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (cls.group_list_url, 'posts/group_list.html'),
            (cls.post_url, 'posts/post_detail.html'),
            (cls.profile_url, 'posts/profile.html'),
        )
        cls.private_urls = (
            ('/create/', 'posts/create_post.html'),
            (cls.post_edit_url, 'posts/create_post.html'),
        )

    def test_anon_public_pages_url_exists(self):
        """
        Проверка что все общие страницы доступны для
        неавторизованного пользователя.
        """
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Ошибка: {name} для {self.anon} не доступен',
                )

    def test_anon_private_pages_url_exists(self):
        """
        Проверка что все приватные страницы недоступны
        для неавторизованного пользователя.
        """
        for pages in self.private_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertEqual(
                    response.status_code,
                    302,
                    f'Ошибка: {url} доступен для неавторизованного'
                    f'пользователя на {name}',
                )

    def test_private_pages_for_authorized_url_exists(self):
        """
        Проверка что все приватные страницы доступны
        для авторизованного пользователя.
        """
        self.client.force_login(self.user)
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Ошибка: {name} для {self.client} не доступен',
                )

    def test_public_urls_uses_correct_template(self):
        """
        Проверка общедоступные url-адреса используют
        соответствующий шаблон.
        """
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertTemplateUsed(
                    response,
                    name,
                    f'Ошибка: {url} ожидал шаблон {name}',
                )

    def test_private_urls_uses_correct_template(self):
        """
        Проверка общедоступные url-адреса
        используют соответствующий шаблон.
        """
        for pages in self.public_urls:
            url, name = pages
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertTemplateUsed(
                    response,
                    name,
                    f'Ошибка: {url} ожидал шаблон {name}',
                )
