# Load items and their related types and categories for the Whohas list.
# Načítá předměty a jejich typy a kategorie pro seznam Whohas.
from django.views import View
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from whohas.forms import ItemForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from whohas.forms import ItemForm

from syscor.views.syscor import SysAuthNoPermission
from whohas.models import ItemCategories, ItemTypes, LoanStatuses


# Display items after checking the user's permission to view them.
# Zobrazuje předměty po kontrole oprávnění k jejich prohlížení.
class ItemCategoriesView(SysAuthNoPermission, View):
    permission_required = "whohas.view_itemcategories"

    # Renders categories with their assigned items.
    # Vykresluje kategorie s přiřazenými předměty.
    def get(self, request):
        Categories = list(
            ItemCategories.objects.all()
            .prefetch_related("items")
            .order_by("item_category_name", "pk")
        )
        web_data = {
            "categories": Categories,
            "table_rows_count": len(Categories),
        }
        return self.page_render(request, "itemcategories", web_data)

# Shows the item type catalogue.
# Zobrazuje číselník typů předmětů.
class ItemTypesView(SysAuthNoPermission, View):
    permission_required = "whohas.view_itemtypes"

    # Renders item types with their assigned items.
    # Vykresluje typy s přiřazenými předměty.
    def get(self, request):
        Types = list(
            ItemTypes.objects.all()
            .prefetch_related("items")
            .order_by("name", "pk")
        )
        web_data = {
            "types": Types,
            "table_rows_count": len(Types),
        }
        return self.page_render(request, "itemtypes", web_data)

# Shows the loan status catalogue.
# Zobrazuje číselník stavů výpůjček.
class LoanStatusesView(SysAuthNoPermission, View):
    permission_required = "whohas.view_loanstatuses"

    # Renders loan statuses with their associated loans.
    # Vykresluje stavy výpůjček se souvisejícími výpůjčkami.
    def get(self, request):
        lstatuses = list(
            LoanStatuses.objects.all()
            .prefetch_related("loans")
            .order_by("name", "pk")
        )
        web_data = {
            "loanstatuses": lstatuses,
            "table_rows_count": len(lstatuses),
        }
        return self.page_render(request, "loanstatuses", web_data)
