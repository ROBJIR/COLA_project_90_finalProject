# Load items and their related types and categories for the Whohas list.
# Načítá předměty a jejich typy a kategorie pro seznam Whohas.
from django.views import View
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from whohas.forms import ItemForm, ItemWriteForm

from syscor.views.syscor import SysAuthNoPermission
from whohas.models import Items
from syscor.views.web import WebMachine, WebRenderMixin


# Display items after checking the user's permission to view them.
# Zobrazuje předměty po kontrole oprávnění k jejich prohlížení.
class ItemsView(SysAuthNoPermission, WebRenderMixin, View):
    permission_required = "whohas.view_items"

    # Fetch types and owners in the main query and categories in one additional query.
    # Načítá typy a vlastníky hlavním dotazem a kategorie jedním dodatečným dotazem.
    def get(self, request):
        items = list(
            Items.objects.select_related("item_type", "owner")
            .prefetch_related("item_categories")
            .order_by("name", "pk")
        )
        web_data = {
            "items": items,
            "table_rows_count": len(items),
        }
        return self.page_render(request, "items", web_data)

# Share item forms and the project's page renderer.
# Sdílí formulář předmětu a projektové vykreslování stránky.
class ItemFormView(SysAuthNoPermission, WebRenderMixin, View):
    # Renders the item form in the requested mode.
    # Vykresluje formulář předmětu v požadovaném režimu.
    def show(self, request, form, item=None, editing=False, creating=False, deleting=False, status=200):
        if not editing:
            for field in form.fields.values():
                field.disabled = True
        response = self.page_render(request, 'itemdetail', {
            'form': form, 'item': item, 'editing': editing,
            'creating': creating, 'deleting': deleting,
            'saved': request.GET.get('saved') == '1',
        })
        response.status_code = status
        return response


# Display and edit an existing item after operation-specific authorization.
# Zobrazuje a upravuje existující předmět po kontrole oprávnění k operaci.
class ItemDetailView(ItemFormView):
    # Requires change permission for edits and view permission for read-only access.
    # Při úpravách vyžaduje oprávnění ke změně, při prohlížení oprávnění ke čtení.
    def get_permission_required(self):
        permissions = ['whohas.view_items']
        if self.request.method == 'POST' or self.request.GET.get('edit') == '1':
            permissions.append('whohas.change_items')
        return permissions

    # Loads the item and selects read-only or edit mode.
    # Načítá předmět a volí režim prohlížení nebo úprav.
    def get(self, request, itemid):
        item = get_object_or_404(Items.objects.select_related("owner"), pk=itemid)
        editing = request.GET.get('edit') == '1'
        form = (
            ItemWriteForm(instance=item, current_user=request.user)
            if editing else ItemForm(instance=item)
        )
        return self.show(request, form, item, editing=editing)

    # Validates and saves changes to the item.
    # Ověřuje a ukládá změny předmětu.
    def post(self, request, itemid):
        item = get_object_or_404(Items, pk=itemid)
        form = ItemWriteForm(request.POST, instance=item, current_user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(reverse('itemdetail', args=[item.pk]) + '?saved=1')
        return self.show(request, form, item, editing=True, status=400)


# Create items and persist their category memberships in the same transaction.
# Vytváří předměty a ukládá jejich kategorie v jedné transakci.
class ItemCreateView(ItemFormView):
    permission_required = ('whohas.view_items', 'whohas.add_items')

    # Displays an empty form for a new item.
    # Zobrazuje prázdný formulář pro nový předmět.
    def get(self, request):
        form = ItemWriteForm(current_user=request.user)
        return self.show(request, form, editing=True, creating=True)

    # Validates and saves the new item.
    # Ověřuje a ukládá nový předmět.
    def post(self, request):
        form = ItemWriteForm(request.POST, current_user=request.user)
        if form.is_valid():
            with transaction.atomic():
                item = form.save()
            return redirect(reverse('itemdetail', args=[item.pk]) + '?saved=1')
        return self.show(request, form, editing=True, creating=True, status=400)


# Show a confirmation page; delete only on an explicit CSRF-protected POST.
# Zobrazuje potvrzení; maže pouze při výslovném POST chráněném proti CSRF.
class ItemDeleteView(ItemFormView):
    permission_required = ('whohas.view_items', 'whohas.delete_items')

    # Displays the item deletion confirmation.
    # Zobrazuje potvrzení smazání předmětu.
    def get(self, request, itemid):
        item = get_object_or_404(Items, pk=itemid)
        return self.show(request, ItemForm(instance=item), item, deleting=True)

    # Deletes the confirmed item when its related records allow it.
    # Po potvrzení maže předmět, pokud to dovolují související záznamy.
    def post(self, request, itemid):
        item = get_object_or_404(Items, pk=itemid)
        if request.POST.get('confirm') != 'yes':
            return self.show(request, ItemForm(instance=item), item, deleting=True, status=400)
        try:
            with transaction.atomic():
                item.delete()
        except ProtectedError:
            WebMachine.web_message_set(
                request,
                "This item cannot be deleted because it has recorded loans.",
                "warning",
            )
            return redirect('itemdetail', itemid=item.pk)
        return redirect('items')
