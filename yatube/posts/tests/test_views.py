import os
import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.list_dir = os.listdir(os.getcwd())
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
        cls.testuser = User.objects.create_user(
            username="testuser", password="123"
        )
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )
        cls.group2 = Group.objects.create(
            title="Тест2",
            slug="Test2",
            description="Тестовое описание2"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст1",
            author=cls.testuser,
            group=cls.group,
            image=uploaded
        )
        cls.templates_pages_names = {
            "posts/index.html": reverse("index"),
            "posts/new.html": reverse("new_post"),
            "group.html": (
                reverse("group_slug", kwargs={
                    "slug": f"{cls.group.slug}"
                })
            ),
        }
        cls.form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        for path in os.listdir(os.getcwd()):
            if path not in cls.list_dir:
                shutil.rmtree(path, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        user = PostPagesTests.testuser
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    def checking_correct_post(self, obj):
        first_object = obj
        post = PostPagesTests.post
        post_id_0 = first_object.id
        text_0 = first_object.text
        author_0 = first_object.author
        group_0 = first_object.group
        image_0 = first_object.image
        self.assertEqual(post_id_0, post.id)
        self.assertEqual(text_0, post.text)
        self.assertEqual(author_0, post.author)
        self.assertEqual(group_0, post.group)
        self.assertEqual(image_0, post.image)

    def checking_correct_group(self, obj):
        first_object = obj
        group = PostPagesTests.group
        title_0 = first_object.title
        slug_0 = first_object.slug
        description_0 = first_object.description
        self.assertEqual(title_0, group.title)
        self.assertEqual(slug_0, group.slug)
        self.assertEqual(description_0, group.description)

    def test_pages_use_correct_template(self):
        for template, reverse_name in \
                PostPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse("new_post"))
        is_new = response.context["is_new"]
        self.assertTrue(is_new)
        for value, expected in PostPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        first_object = response.context["page"][0]
        self.checking_correct_post(first_object)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("group_slug", kwargs={
                "slug": f"{PostPagesTests.group.slug}"
            })
        )
        first_object = response.context["group"]
        self.checking_correct_group(first_object)
        second_object = response.context["page"][0]
        self.checking_correct_post(second_object)

    def test_index_page_on_expected_objects(self):
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(len(response.context["page"]), 1)

    def test_group_page_on_expected_objects(self):
        response = self.authorized_client.get(
            reverse("group_slug", kwargs={
                "slug": f"{PostPagesTests.group.slug}"
            })
        )
        self.assertEqual(len(response.context["page"]), 1)

    def test_post_for_another_group_page(self):
        response = self.authorized_client.get(
            reverse("group_slug", kwargs={
                "slug": f"{PostPagesTests.group2.slug}"
            })
        )
        self.assertEqual(len(response.context["page"]), 0)

    def test_cache_index(self):
        form_data_for_cache = {
            "text": "Проверка кэша",
        }
        self.authorized_client.post(
            reverse("new_post"),
            data=form_data_for_cache,
            follow=True
        )
        response = self.authorized_client.get(reverse("index"))
        self.assertNotContains(response, "Проверка кэша")
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        self.assertContains(response, "Проверка кэша")


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser1 = User.objects.create_user(
            username="testuser1", password="123"
        )
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )
        i = 0
        while i < 15:
            cls.post = Post.objects.create(
                text=f"Тест {i}",
                author=cls.testuser1,
                group=cls.group
            )
            i += 1

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 5)

    def test_group_first_page_contains_twelve_records(self):
        response = self.client.get(
            reverse("group_slug", kwargs={
                "slug": f"{PaginatorViewsTest.group.slug}"})
        )
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_group_second_page_contains_three_records(self):
        response = self.client.get(
            reverse("group_slug", kwargs={
                "slug": f"{PaginatorViewsTest.group.slug}"}) + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 5)


class ProfilePagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.list_dir = os.listdir(os.getcwd())
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
        cls.testuser = User.objects.create_user(
            username="testuser", password="123",
            first_name="name", last_name="surname"
        )
        cls.group = Group.objects.create(
            title="Тест",
            slug="Test",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст1",
            author=cls.testuser,
            group=cls.group,
            image=uploaded
        )
        cls.form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        for path in os.listdir(os.getcwd()):
            if path not in cls.list_dir:
                shutil.rmtree(path, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        user = PostPagesTests.testuser
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.guest_client = Client()

    def checking_correct_post(self, obj):
        first_object = obj
        post = ProfilePagesTests.post
        post_id_0 = first_object.id
        text_0 = first_object.text
        author_0 = first_object.author
        group_0 = first_object.group
        image_0 = first_object.image
        self.assertEqual(post_id_0, post.id)
        self.assertEqual(text_0, post.text)
        self.assertEqual(author_0, post.author)
        self.assertEqual(group_0, post.group)
        self.assertEqual(image_0, post.image)

    def checking_correct_user(self, obj):
        second_object = obj
        testuser = ProfilePagesTests.testuser
        username_1 = second_object.username
        full_name_1 = second_object.get_full_name()
        post_count_1 = second_object.posts.count()
        self.assertEqual(username_1, testuser.username)
        self.assertEqual(full_name_1, testuser.get_full_name())
        self.assertEqual(post_count_1, testuser.posts.count())

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("profile", args=[
                f"{ProfilePagesTests.post.author}"
            ])
        )
        first_object = response.context["page"][0]
        self.checking_correct_post(first_object)
        second_object = response.context["author_card"]
        self.checking_correct_user(second_object)

    def test_post_view_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "post_view", kwargs={
                    "username": f"{ProfilePagesTests.post.author}",
                    "post_id": f"{ProfilePagesTests.post.id}"
                })
        )
        first_object = response.context["post"]
        self.checking_correct_post(first_object)
        second_object = response.context["author_card"]
        self.checking_correct_user(second_object)

    def test_post_edit_page_show_correct_context(self):
        self.authorized_client.login(username="testuser", password="123")
        response = self.authorized_client.get(
            reverse(
                "post_edit", kwargs={
                    "username": f"{ProfilePagesTests.post.author}",
                    "post_id": f"{ProfilePagesTests.post.id}"}
            )
        )
        for value, expected in ProfilePagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)


class FollowCommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(
            username="follower", password="123",
        )
        cls.another_follower = User.objects.create_user(
            username="another_follower", password="531",
        )
        cls.following = User.objects.create_user(
            username="following", password="321",
        )
        cls.post = Post.objects.create(
            text="test post",
            author=cls.following
        )

    def setUp(self):
        follower = FollowCommentTests.follower
        another_follower = FollowCommentTests.another_follower
        following = FollowCommentTests.following
        self.follower_client = Client()
        self.follower_client.force_login(follower)
        self.another_follower_client = Client()
        self.another_follower_client.force_login(another_follower)
        self.following_client = Client()
        self.following_client.force_login(following)
        self.guest_user_client = Client()

    def test_follow_unfollow(self):
        self.follower_client.get(
            reverse(
                "profile_follow",
                kwargs={"username": FollowCommentTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.follower_client.get(
            reverse(
                "profile_unfollow",
                kwargs={"username": FollowCommentTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_page(self):
        self.follower_client.get(
            reverse(
                "profile_follow",
                kwargs={"username": FollowCommentTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        form_data_for_follow_page = {
            "text": "Пост для подписчика"
        }
        self.following_client.post(
            reverse(
                "new_post"
            ),
            data=form_data_for_follow_page,
            follow=True
        )
        response = self.follower_client.get(reverse("follow_index"))
        self.assertContains(response, "Пост для подписчика")
        response = self.another_follower_client.get(reverse("follow_index"))
        self.assertNotContains(response, "Пост для подписчика")

    def test_comment(self):
        self.follower_client.post(
            f"/{FollowCommentTests.following.username}/"
            f"{FollowCommentTests.post.id}/comment",
            {"text": "Тестовый комментарий"}
        )
        response = self.follower_client.get(
            f"/{FollowCommentTests.following.username}/"
            f"{FollowCommentTests.post.id}/"
        )
        self.assertContains(response, "Тестовый комментарий")
        self.guest_user_client.post(
            f"/{FollowCommentTests.following.username}/"
            f"{FollowCommentTests.post.id}/comment",
            {"text": "Комментарий гостя"}
        )
        response = self.guest_user_client.get(
            f"/{FollowCommentTests.following.username}/"
            f"{FollowCommentTests.post.id}/"
        )
        self.assertNotContains(response, "Комментарий гостя")
