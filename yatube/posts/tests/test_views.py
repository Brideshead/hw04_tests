from turtle import title
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms  

from posts.models import Post, Group

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text = 'Тестовый пост',
            group = cls.group,
            author = cls.user)

        cls.guest_client = Client()
        cls.author_client = Client()    

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = PostViewTests.user
        # Создаем второй клиент
        self.authorized_client_author = Client()
        # Авторизуем пользователя
        self.authorized_client_author.force_login(self.user)
        self.user_not_author = User.objects.create(username='not_author')
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author) 

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': self.user.username}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name = reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                error_name = f'Ошибка: {reverse_name} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('posts:index'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        first_text = first_object.text
        first_group = first_object.group
        self.assertEqual(first_text, self.post.text)
        self.assertEqual(str(first_group), self.group.title)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        first_object = response.context['page_obj'][0]
        first_author = first_object.author
        first_text = first_object.text
        first_group = first_object.group
        self.assertEqual(first_author, self.post.author)
        self.assertEqual(first_text, self.post.text)
        self.assertEqual(str(first_group), self.group.title)    

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом.""" 
        response = self.authorized_client_author.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        first_author = first_object.author
        first_text = first_object.text
        first_group = first_object.group
        self.assertEqual(first_author, self.post.author)
        self.assertEqual(first_text, self.post.text)
        self.assertEqual(str(first_group), self.group.title)   

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""          
        response = self.authorized_client_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('post').pk, self.post.pk)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get(
            'post').author, self.post.author)
        self.assertEqual(response.context.get(
            'post').group, self.post.group)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post для создания поста сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_show_correct_contect(self):
        """Пост отображается корректно , если во время его создания, указать группу"""
        test_user = User.objects.create(username='test_author')
        test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        test_post = Post.objects.create(
            text = 'Новый тестовый пост',
            author = test_user,
            group = test_group,
        )

        list_page_name = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': test_group.slug}),
            reverse('posts:profile', kwargs={'username':'test_author'}),
        )
        for name_page in list_page_name:
            with self.subTest(name_page=name_page):
                response = self.authorized_client_author.get(name_page)
                first_object = response.context['page_obj'][0]
                response = self.authorized_client_author.get(
                    reverse('posts:group_list', kwargs={'slug': self.group.slug})
                )
                group_test_slug = response.context['page_obj'][0]
                self.assertEqual(first_object, test_post)
                self.assertNotEqual(first_object, group_test_slug)



class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='post_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',)
        for cls.post_number in range(15):
            cls.post_fill = Post.objects.create(
                text=f'Пост {cls.post_number} в тесте!',
                group=cls.group,
                author=cls.user,)
        
    def test_first_page_index_contains_ten_records(self):
        """Пагинатор выводит для index 10 постов на первую страницу."""
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_five_records(self):
        """Пагинатор выводит для index 5 постов на вторую страницу."""
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_group_list_contains_ten_records(self):
        """Пагинатор выводит для group_list 10 постов на первую страницу."""
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        # Проверка: количество постов на первой странице равно 10. 
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_five_records(self):
        """Пагинатор выводит для group_list 5 постов на вторую страницу."""
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)  

    def test_first_page_profile_contains_ten_records(self):
        """Пагинатор выводит для profile 10 постов на первую страницу."""
        response = self.client.get(reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_five_records(self):
        """Пагинатор выводит для profile 5 постов на вторую страницу."""
        response = self.client.get(reverse('posts:profile', kwargs={'username': self.user.username}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)       
        
 