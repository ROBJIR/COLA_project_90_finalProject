# Share login, permission checks, and custom forbidden-page rendering across log views.
# Sdílí přihlašování, kontroly oprávnění a vykreslování vlastní stránky zakázaného přístupu mezi pohledy logů.
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from syscor.views.web import WebMachine


# Share access checks and custom 403 responses.
# Sdílí kontroly přístupu a vlastní odpovědi 403.
class SysLogBase(LoginRequiredMixin, PermissionRequiredMixin):
    """Require login and permissions, rendering the application's 403 page."""

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        response = WebMachine.web_renderer(self, self.request, "403")
        response.status_code = 403
        return response
