# Validate editable authentication fields and restrict elevated user access.
# Ověřuje upravitelné údaje autentizace a omezuje správu zvýšených práv uživatele.
from django import forms
from django.contrib.auth.models import User, Group, Permission


# Validate account data and hide privileged fields from non-superusers.
# Ověřuje údaje účtu a skrývá privilegovaná pole před běžnými správci.
class UserDetailForm(forms.ModelForm):
    # Configure model fields and their form help text.
    # Nastavuje modelová pole a jejich nápovědu ve formuláři.
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active',
                  'is_staff', 'is_superuser', 'groups', 'user_permissions')

    # Initialize fields and restrict elevated access to superusers.
    # Inicializuje pole a omezuje správu zvýšených práv na superuživatele.
    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        # Only superusers may manage elevated access or permission assignments.
        # Pouze superuživatel smí měnit zvýšená práva a jejich přiřazení.
        self.fields['user_permissions'].queryset = Permission.objects.select_related('content_type')
        if not actor.is_superuser:
            for name in ('is_staff', 'is_superuser', 'groups', 'user_permissions'):
                del self.fields[name]


# Validate group names and assigned permissions.
# Ověřuje názvy skupin a přiřazená oprávnění.
class GroupDetailForm(forms.ModelForm):
    # Load content types with permissions to avoid a query for each option label.
    # Načítá typy obsahu společně s oprávněními bez dotazu pro každý popisek volby.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.select_related('content_type')

    # Configure model fields and their form help text.
    # Nastavuje modelová pole a jejich nápovědu ve formuláři.
    class Meta:
        model = Group
        fields = ('name', 'permissions')
        help_texts = {
            'permissions': 'Permissions assigned here are inherited by every member of this group.',
        }


# Validate permission identity and uniqueness.
# Ověřuje identitu a jedinečnost oprávnění.
class PermissionDetailForm(forms.ModelForm):
    # Configure model fields and their form help text.
    # Nastavuje modelová pole a jejich nápovědu ve formuláři.
    class Meta:
        model = Permission
        fields = ('name', 'codename', 'content_type')
        help_texts = {
            'codename': 'Changing this code can break existing permission checks in the application.',
            'content_type': 'The application and model this permission belongs to. Changing it changes the permission identity.',
        }
