from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        testuser = User.objects.create_user(
            username="testuser", password="123"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст1 Текстовый текст",
            author=testuser
        )

    def test_post_model_text(self):
        post = PostModelTest.post
        text = post.text[:15]
        self.assertEquals(text, "Тестовый текст1")

    def test_str_post_model(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )

    def test_group_model_title(self):
        group = GroupModelTest.group
        title = group.title
        self.assertEquals(title, "Тест")

    def test_str_group_model(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)
