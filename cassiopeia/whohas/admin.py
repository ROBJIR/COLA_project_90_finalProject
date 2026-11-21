# Configure Django admin lists, filters, and searches for application and web logs.
# Nastavuje seznamy, filtry a vyhledávání aplikačních a webových logů v administraci Django.
from django.contrib import admin
from .models import Events, ItemCategories, Items, ItemTypes, Loans, LoanStatuses, WhohasHomePage


@admin.register(WhohasHomePage)
# Configure application log administration.
# Nastavuje administraci aplikačních logů.
class WhohasHomePage(admin.ModelAdmin):
    list_display = (
        'article_code',
        'article_sequence',
        'aticle_content'
    )
    list_filter = ('article_code', 'article_sequence', 'aticle_content')
    search_fields = ('article_code', 'article_sequence')
    ordering = ('article_sequence',)

# Configures the item type list in Django admin.
# Nastavuje seznam typů předmětů v administraci Django.
@admin.register(ItemTypes)
class ItemTypesAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
    # Stores metadata declared for the item type admin class.
    # Obsahuje metadata deklarovaná pro administraci typů předmětů.
    class Meta:
        verbose_name = "ItemType"
        verbose_name_plural = "ItemTypess"
    # Returns the configured label for the item type.
    # Vrací nastavené označení typu předmětu.
    def __str__(self):
        return self.name


# Configures item categories in Django admin.
# Nastavuje kategorie předmětů v administraci Django.
@admin.register(ItemCategories)
class ItemCategoriesAdmin(admin.ModelAdmin):
    list_display = ("id", "item_category_name")
    search_fields = ("item_category_name",)
    ordering = ("item_category_name",)
    # Stores metadata declared for the category admin class.
    # Obsahuje metadata deklarovaná pro administraci kategorií.
    class Meta:
        verbose_name = "ItemCategory"
        verbose_name_plural = "ItemCategories"

# Configures item records in Django admin.
# Nastavuje záznamy předmětů v administraci Django.
@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "item_type", "owner")
    list_filter = ("item_type", "item_categories")
    search_fields = ("name", "description")
    ordering = ("name",)
    # Stores metadata declared for the item admin class.
    # Obsahuje metadata deklarovaná pro administraci předmětů.
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    # Přehledný výběr více kategorií při editaci.
    filter_horizontal = ("item_categories",)

    # Načte typy a vlastníky společně s předměty bez dotazu pro každý řádek.
    list_select_related = ("item_type", "owner")


# Configures loan statuses in Django admin.
# Nastavuje stavy výpůjček v administraci Django.
@admin.register(LoanStatuses)
class LoanStatusesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "format")
    search_fields = ("name",)
    ordering = ("name",)


# Configures loan records in Django admin.
# Nastavuje výpůjčky v administraci Django.
@admin.register(Loans)
class LoansAdmin(admin.ModelAdmin):
    list_display = (
        "item", "borrower", "status", "tstamp_planned_start",
        "tstamp_planned_end", "tstamp_real_start", "tstamp_real_end",
    )
    list_select_related = ("item", "borrower", "status")
    list_filter = ("status", "tstamp_planned_start")
    search_fields = ("description", "item__name")
    ordering = ("-tstamp_planned_start", "-pk")


# Configures loan events in Django admin.
# Nastavuje události výpůjček v administraci Django.
@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ("id", "tstamp", "loan", "author", "description")
    list_select_related = ("author", "loan")
    list_filter = ("tstamp",)
    search_fields = ("description", "loan__name")
    ordering = ("-tstamp", "-pk")
