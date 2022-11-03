from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    """
    Устанавливаем данные для тестирования posts/forms.

    NUMBER_OF_CONTEXT: индекс извлекаемого контекстного значения.
    """

    NUMBER_OF_CONTEXT: int = 0

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
            text='test_text',
            group=cls.group,
            author=cls.user,
        )
        cls.anon = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user)
        cls.authorized_client_not_author = Client()
        cls.user_not_author = User.objects.create_user(username='not_author')
        cls.authorized_client_not_author.force_login(cls.user_not_author)
        cls.index_url = ('posts:index', 'posts/index.html', None)
        cls.group_list_url = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.group.slug,),
        )
        cls.profile_url = (
            'posts:profile',
            'posts/profile.html',
            (cls.user.username,),
        )
        cls.post_detail_url = (
            'posts:post_detail',
            'posts/post_detail.html',
            (cls.post.pk,),
        )
        cls.post_create_url = (
            'posts:post_create',
            'posts/create_post.html',
            None,
        )
        cls.post_edit_url = (
            'posts:post_edit',
            'posts/create_post.html',
            (cls.post.pk,),
        )
        cls.paginated = (
            cls.index_url,
            cls.group_list_url,
            cls.profile_url,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = (
            self.index_url,
            self.group_list_url,
            self.profile_url,
            self.post_create_url,
            self.post_edit_url,
        )
        for pages in templates_pages_names:
            name, template, arg = pages
            reverse_name = reverse(name, args=arg)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                error_name = f'Ошибка: {reverse_name} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('posts:index'))
        first_object = response.context['post']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(str(first_object.group), self.group.title)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(str(first_object.group), self.group.title)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][
            self.NUMBER_OF_CONTEXT
        ]
        first_author = first_object.author
        first_text = first_object.text
        first_group = first_object.group
        self.assertEqual(first_author, self.post.author)
        self.assertEqual(first_text, self.post.text)
        self.assertEqual(str(first_group), self.group.title)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_detail', args=(self.post.pk,)))
        self.assertEqual(response.context.get('post').pk, self.post.pk)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get(
            'post').author, self.post.author)
        self.assertEqual(response.context.get(
            'post').group, self.post.group)

    def test_create_post_show_correct_context(self):
        """
        Шаблон create_post для создания поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client_author.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', args=(self.post.pk,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_show_correct_context(self):
        """
        Пост отображается корректно,
        если во время его создания, указать группу.
        """
        test_user = User.objects.create_user(
            username='test_author_created_post',
        )
        test_group = mixer.blend(Group)
        test_post = Post.objects.create(
            text='test_text_created_post',
            author=test_user,
            group=test_group,
        )
        list_page_name = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                args=(test_group.slug,),
            ),
            reverse(
                'posts:profile',
                args=(test_user.username,),
            ),
        )
        for name_page in list_page_name:
            with self.subTest(name_page=name_page):
                response = self.authorized_client_author.get(name_page)
                first_object = response.context['page_obj'][
                    self.NUMBER_OF_CONTEXT
                ]
                response = self.authorized_client_author.get(
                    reverse(
                        'posts:group_list',
                        args=(self.group.slug,),
                    ),
                )
                group_test_slug = response.context['page_obj'][
                    self.NUMBER_OF_CONTEXT
                ]
                self.assertEqual(first_object, test_post)
                self.assertNotEqual(first_object, group_test_slug)


class PaginatorViewsTest(TestCase):
    """
    Тестирование паджинации.
    Здесь создаются фикстуры: клиент и
    15 тестовых записей NUMBER_OF_POSTS.

    NUMBER_OF_POSTS_SECOND_PAGE: количество выводимых
    постов для второй страницы.
    """

    NUMBER_OF_POSTS: int = 15
    NUMBER_OF_POSTS_SECOND_PAGE: int = 5

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = mixer.blend(Group)
        for cls.post_number in range(cls.NUMBER_OF_POSTS):
            cls.post_fill = Post.objects.create(
                text=f'Пост {cls.post_number} в тесте!',
                group=cls.group,
                author=cls.user,
            )
        cls.paginated = (
            ('posts:index', 'posts/index.html', None),
            ('posts:profile', 'posts/profile.html', (cls.user.username,)),
            ('posts:group_list', 'posts/group_list.html', (cls.group.slug,)),
        )

    def test_first_and_second_page_paginate_correct(self):
        """Проверка вывода количества постов на первую и вторую страницы."""
        for pages in self.paginated:
            name, template, arg = pages
            reverse_name = reverse(name, args=arg)
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.LIMIT_POSTS,
                    f'Ошибка: Пагинатор не выводит на первую страницу'
                    f'{template} 10 постов',
                )
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.NUMBER_OF_POSTS_SECOND_PAGE,
                    f'Ошибка: Пагинатор не выводит на вторую страницу'
                    f'{template} 5 постов',
                )
