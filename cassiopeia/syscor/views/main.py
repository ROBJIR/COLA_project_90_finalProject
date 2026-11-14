from django.views import View
from .web import WebMachine

class MainView(View):
    def __init__(self):
        self.web_page_attributes = {
                  "application_code": "cassiopeia"
                , "application_name": "Cassiopeia Projects"
                , "module_code": "cassiopeia"
                , "module_template": "syscor-main.html"
                , "module_name": "Cassiopeia Project"}
        self.web_data = {}
    def get(self, request):
        return WebMachine.web_renderer(self, request, 'cassiopeia', self.web_data)