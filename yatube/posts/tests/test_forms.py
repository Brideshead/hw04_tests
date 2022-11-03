from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from mixer.backend.django import mixer

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
        cls.anon = Client()
        cls.client_author = Client()
        cls.client_not_author = Client()
        cls.group = mixer.blend(Group)
        cls.user = User.objects.create_user(username='test_author')
        cls.user_not_author = User.objects.create(username='not_author')

    def test_post_create_authorized_user(self):
        """Пост создаётся для авторизованного пользователя."""
        self.client_author.force_login(self.user)
        posts_count = Post.objects.count()
        response = self.client_author.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый пост',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.latest('id').text, 'Тестовый пост')
        self.assertEqual(Post.objects.latest('id').author, self.user)
        self.assertEqual(Post.objects.latest('id').group.pk, self.group.pk)

    def test_post_create_not_authorized_user(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        response = self.anon.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый пост',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse('posts:post_create'),
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit_authorized_user_author(self):
        """Проверка редактирования записи авторизированным клиентом."""
        self.client_author.force_login(self.user)
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        response = self.client_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk},
            ),
            data={
                'text': 'Отредактированный текст поста',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.latest('pk').text == 'Отредактированный текст поста')
        self.assertTrue(Post.objects.latest('pk').author == self.user)
        self.assertTrue(Post.objects.latest('pk').group.pk == self.group.pk)

    def test_post_edit_authorized_no_author(self):
        """
        Проверка, что пост не редактируется авторизованным
        пользователем - не автором поста.
        """
        self.client_not_author.force_login(self.user_not_author)
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        response = self.client_not_author.post(
            reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
            data={
                'text': 'Тестовый пост',
                'group': self.group.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('pk')
        self.assertFalse(post.text == 'Тестовый пост')
        self.assertTrue(post.author == self.user)
        self.assertTrue(post.group.pk == self.group.pk)

    def test_post_edit_anon_user(self):
        """Проверка редактирования поста неавторизованным пользователем."""
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.anon.post(
            reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('login')
            + '?next='
            + reverse(
                'posts:post_edit',
                args=(post.pk,),
            ),
        )
