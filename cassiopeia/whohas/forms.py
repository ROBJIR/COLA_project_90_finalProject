# Validate editable item fields and their catalogue relationships.
# Ověřuje upravitelné údaje předmětu a vazby na číselníky.
from django import forms
from whohas.models import Items, Loans


# Defines the shared model form for items.
# Definuje společný modelový formulář předmětů.
class ItemForm(forms.ModelForm):
    # Declares the model and fields used by the form.
    # Určuje model a pole používané formulářem.
    class Meta:
        model = Items
        fields = ('name', 'description', 'item_type', 'item_categories')
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    # Configures fields and widgets for display.
    # Nastavuje pole a ovládací prvky pro zobrazení.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_categories'].label_from_instance = lambda category: category.item_category_name or f'Category #{category.pk}'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


# Adds the editable owner field for item creation and updates.
# Přidává upravitelné pole vlastníka pro vytváření a úpravy předmětů.
class ItemWriteForm(ItemForm):
    # Extends the inherited form metadata with the owner field.
    # Rozšiřuje zděděná metadata formuláře o pole vlastníka.
    class Meta(ItemForm.Meta):
        fields = (*ItemForm.Meta.fields, 'owner')

    # Configures owner choices and the current user default.
    # Nastavuje volby vlastníka a výchozího aktuálního uživatele.
    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        if self.instance.owner_id is None:
            self.initial['owner'] = current_user.pk
        self.fields['owner'].label_from_instance = lambda user: (
            f'{user.get_full_name()} ({user.get_username()})'
            if user.get_full_name() else user.get_username()
        )

    # Returns the selected owner or the current user.
    # Vrací vybraného vlastníka nebo aktuálního uživatele.
    def clean_owner(self):
        return self.cleaned_data['owner'] or self.current_user


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loans
        fields = (
            'item', 'status', 'borrower',
            'tstamp_planned_start', 'tstamp_planned_end',
            'tstamp_real_start', 'tstamp_real_end', 'description',
        )
        labels = {
            'tstamp_planned_start': 'Planned start',
            'tstamp_planned_end': 'Planned end',
            'tstamp_real_start': 'Actual start',
            'tstamp_real_end': 'Actual end',
        }
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(
                    format='%Y-%m-%dT%H:%M:%S',
                    attrs={'type': 'datetime-local', 'step': '1'},
                )
            field.widget.attrs['class'] = (
                'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            )
