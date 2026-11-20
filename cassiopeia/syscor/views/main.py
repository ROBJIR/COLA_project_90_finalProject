from django.views import View
from .web import WebRenderMixin

# Shows the Cassiopeia landing page.
# Zobrazuje úvodní stránku Cassiopeji.
class MainView(WebRenderMixin, View):
    # Initializes page attributes and context.
    # Inicializuje atributy a kontext stránky.
    def __init__(self):
        self.web_page_attributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "cassiopeia"
                , "module_template": "syscor-main.html"
                , "module_name": "Cassiopeia Project"}
        self.web_data = {}
    # Renders the Cassiopeia home page.
    # Vykresluje úvodní stránku Cassiopeji.
    def get(self, request):
        return self.page_render(request, 'cassiopeia', self.web_data)