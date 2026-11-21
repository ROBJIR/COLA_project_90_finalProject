
from django.shortcuts import render
from django.views import View

from .auth import SysAuthNoPermission

class WebMainRender(SysAuthNoPermission, View):
    def get(self, request):
        web_page_attributes = {}
        web_page_attributes["application_code"], web_page_attributes["module_code"], template_name, records = self.data_prepare()
        web_page_attributes["application_name"] = web_page_attributes["application_code"]
        web_page_attributes["module_name"] = web_page_attributes["module_code"].lower()
        web_page_attributes["module_name"] = web_page_attributes["module_code"]
        web_page_attributes["application_module_start"] = web_page_attributes["module_code"]
        web_page_attributes["module_file_template"] = web_page_attributes["module_code"]
        web_page_attributes["application_file_menu"] = f"{web_page_attributes["application_code"]}-menu-dropdown.html"
        web_data = {}
        web_data["records"] = records
        web_data["records_num_rows"] = len(records)
        return render(request, template_name, {"web_page_attributes":web_page_attributes,"web_data": web_data })
