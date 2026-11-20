from django.db import models


# Stores content for the Paidyet home page.
# Ukládá obsah úvodní stránky Paidyet.
class PaidyetHomePage(models.Model):
     article_code = models.CharField(max_length=24, null=True)
     article_sequence = models.PositiveIntegerField(null=False)
     aticle_content = models.TextField(null=True)