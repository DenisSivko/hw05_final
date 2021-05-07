import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.testuser = User.objects.create_user(
            username="testuser", password="123"
        )
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст1",
            author=cls.testuser,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        user = PostFormTests.testuser
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        cache.clear()

    def test_new_post(self):
        post_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        form_data = {
            "text": "Текст из формы",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            "text": "Изменили текст",
        }
        response = self.authorized_client.post(
            reverse(
                "post_edit", kwargs={
                    "username": f"{PostFormTests.testuser.username}",
                    "post_id": f"{PostFormTests.post.id}"}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            "post_view", kwargs={
                "username": f"{PostFormTests.testuser.username}",
                "post_id": f"{PostFormTests.post.id}"})
        )
        self.assertEqual(Post.objects.count(), post_count)
