from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create_user(
            username="testuser", password="123"
        )
        cls.not_author = User.objects.create_user(
            username="not_author", password="321"
        )
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст1",
            author=cls.testuser
        )
        cls.templates_auth_users_url_names = (
            ("/new/", "posts/new.html"),
            (f"/{cls.post.author}/{cls.post.id}/edit/",
             "posts/new.html")
        )
        cls.templates_no_auth_users_url_names = (
            ("/", "posts/index.html"),
            (f"/group/{cls.group.slug}/", "group.html"),
            (f"/{cls.post.author}/", "posts/profile.html"),
            (f"/{cls.post.author}/{cls.post.id}/", "posts/post.html")
        )
        cls.templates_url_names = (
            *cls.templates_auth_users_url_names,
            *cls.templates_no_auth_users_url_names
        )

    def setUp(self):
        self.guest_client = Client()
        user = PostsURLTests.testuser
        user2 = PostsURLTests.not_author
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(user2)

    def test_urls_uses_correct_template(self):
        for adress, template in PostsURLTests.templates_url_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_user(self):
        for adress, template in PostsURLTests.templates_url_names:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_anonymous_user(self):
        for adress, template in PostsURLTests.templates_auth_users_url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertRedirects(response, ("/auth/login/?next=" + adress))

    def test_urls_edit_page_authorized_user_but_not_author(self):
        response = self.authorized_client_not_author.get(
            f"/{PostsURLTests.post.author}/{PostsURLTests.post.id}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f"/{PostsURLTests.post.author}/{PostsURLTests.post.id}/"
        )

    def test_url_404_code(self):
        response = self.guest_client.get("/404/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
