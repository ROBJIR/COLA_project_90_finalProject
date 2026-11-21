from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Meta


class MetaViewTests(TestCase):
    def test_renders_meta_articles(self):
        admin = get_user_model().objects.create_superuser("meta_admin")
        self.client.force_login(admin)
        url = reverse("meta")

        self.assertContains(self.client.get(url), "No records found.")

        Meta.objects.create(article_sequence=1, aticle_content="Meta test article")
        self.assertContains(self.client.get(url), "Meta test article")
