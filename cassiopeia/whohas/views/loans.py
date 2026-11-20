from django.shortcuts import get_object_or_404
from django.views import View
from syscor.views.syscor import SysAuthNoPermission
from whohas.models import Loans

# Shows the loan list to authorized users.
# Zobrazuje seznam výpůjček oprávněným uživatelům.
class LoansView(SysAuthNoPermission, View):
    permission_required = "whohas.view_loans"

    # Loads loans and renders the list.
    # Načítá výpůjčky a vykresluje seznam.
    def get(self, request):
        loans = list(
            Loans.objects.select_related("item","borrower","status")
            .order_by("tstamp_real_start", "pk")
        )
        web_data = {
            "loans": loans,
            "table_rows_count": len(loans),
        }
        return self.page_render(request, "loans", web_data)

# Shows the detail view for a selected loan.
# Zobrazuje pohled pro detail vybrané výpůjčky.
class LoanDetailView(SysAuthNoPermission, View):
    permission_required = "whohas.view_loans"

    # Loads the loan and its event history.
    # Načítá výpůjčku a historii událostí.
    def get(self, request, loanid):
        loan = get_object_or_404(
            Loans.objects.select_related("item", "borrower", "status"), pk=loanid,
        )
        events = loan.loan.select_related("author").order_by("tstamp", "pk")
        return self.page_render(request, "loandetail", {"loan": loan, "events": events})
