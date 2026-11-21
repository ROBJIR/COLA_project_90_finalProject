from django.db.models import Exists, OuterRef
from django.views import View

from syscor.views.syscor import SysAuthNoPermission
from whohas.models import Items, Loans

# Shows the Whohas landing page.
# Zobrazuje úvodní stránku Whohas.
class WhohasView(SysAuthNoPermission, View):
    permission_required = "whohas.view_whohashomepage"

    # Renders the Whohas home page.
    # Vykresluje úvodní stránku Whohas.
    def get(self, request):
        web_data = {}
        web_data["itemsfree"] = self.itemfree()
        web_data["loansover"] = self.overdue_loans()
        return self.page_render(request, "whohas", web_data)

    @staticmethod
    def itemfree():
        open_loans = Loans.objects.filter(
            item_id=OuterRef("pk"), tstamp_real_end__isnull=True,
        )
        return (
            Items.objects.filter(~Exists(open_loans))
            .select_related("item_type")
            .order_by("name", "pk")
        )

    @staticmethod
    def overdue_loans():
        return Loans.objects.filter(status__name="success").order_by("tstamp_planned_end", "pk")
