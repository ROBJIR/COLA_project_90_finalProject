
from django.contrib import admin
from .models import PaidyetHomePage


@admin.register(PaidyetHomePage)
# Configures editing and ordering of Paidyet home page articles.
# Nastavuje úpravy a řazení článků na úvodní stránce Paidyet.
class PaidyetHomePage(admin.ModelAdmin):
    list_display = (
        'article_code',
        'article_sequence',
        'aticle_content'
    )
    list_filter = ('article_code', 'article_sequence', 'aticle_content')
    search_fields = ('article_code', 'article_sequence')
    ordering = ('article_sequence',)