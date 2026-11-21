from django.shortcuts import get_object_or_404, redirect
from django.views import View
from syscor.views.syscor import SysAuthNoPermission
from whohas.forms import LoanForm
from whohas.models import Loans
from whohas.views.whohas import WhohasView

# Shows the loan list to authorized users.
# Zobrazuje seznam výpůjček oprávněným uživatelům.
class LoansView(SysAuthNoPermission, View):
    permission_required = "whohas.view_loans"
    title = "Loans"
    def get_queryset(self):
        return Loans.objects.order_by("tstamp_real_start", "pk")

    # Loads loans and renders the list.
    # Načítá výpůjčky a vykresluje seznam.
    def get(self, request):
        loans = list(
            self.get_queryset()
            .select_related("item__item_type", "borrower", "status")
            .prefetch_related("loan")
        )
        web_data = {
            "loans": loans,
            "table_rows_count": len(loans),
            "title": self.title,
        }
        return self.page_render(request, "loans", web_data)


class OverdueLoansView(LoansView):
    title = "Overdue loans"

    def get_queryset(self):
        return WhohasView.overdue_loans()


# Shows the detail view for a selected loan.
# Zobrazuje pohled pro detail vybrané výpůjčky.
class LoanDetailView(SysAuthNoPermission, View):
    def get_permission_required(self):
        permissions = ["whohas.view_loans"]
        if self.request.method == "POST" or self.request.GET.get("edit") == "1":
            permissions.append("whohas.change_loans")
        return permissions

    def get(self, request, loanid):
        loan = get_object_or_404(
            Loans.objects.select_related("item", "borrower", "status"), pk=loanid,
        )
        form = LoanForm(instance=loan) if request.GET.get("edit") == "1" else None
        return self.show(request, loan, form)

    def post(self, request, loanid):
        loan = get_object_or_404(Loans, pk=loanid)
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            if form.has_changed():
                loan = form.save(commit=False)
                loan.save(update_fields=form.changed_data)
            return redirect("loandetail", loanid=loan.pk)
        return self.show(request, loan, form, status=400)

    def show(self, request, loan, form, status=200):
        events = loan.loan.select_related("author").order_by("tstamp", "pk")
        response = self.page_render(
            request, "loandetail", {"loan": loan, "events": events, "form": form},
        )
        response.status_code = status
        return response
