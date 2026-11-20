from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from syscor.views.web import WebMachine, WebRenderMixin

# Share access checks and custom 403 responses.
# Sdílí kontroly přístupu a vlastní odpovědi 403.
class SysAuthNoPermission(LoginRequiredMixin, PermissionRequiredMixin, WebRenderMixin):
    """Require login and permissions, rendering the application's 403 page."""

    # Redirects anonymous users and renders a 403 page for authenticated users.
    # Přesměrovává nepřihlášené uživatele a přihlášeným vykresluje stránku 403.
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            WebMachine.web_message_set(self.request,
                                       message_body='You must be logged on access for web page.',
                                       message_alert='warning', message_type='web')
            return super().handle_no_permission()

        response = self.page_render(self.request, "403")
        response.status_code = 403
        return response
