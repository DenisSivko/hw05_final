from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AboutPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_pages_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_pages_use_correct_template(self):
        for template, reverse_name in \
                AboutPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_anonymous_user(self):
        for adress in AboutPagesTests.templates_pages_names.values():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertEqual(response.status_code, 200)
