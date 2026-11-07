import sys
from django.utils.html import format_html, format_html_join

class SysInfoBase():
    def __init__(self):
        self.webpageattributes = {
              "application_code": "sysinfo"
            , "application_name": "System Informations"
            , "module_code":      "sysinfo"
            , "module_template":  "sysinfo.html"
            , "module_name":      "System Informations"}
        self.webdata = {"webmain":""}
    def SysInfoSystem(self):
        self.sysinfosystem = {
            "version": sys.version,
            "executable": sys.executable
        }
        return self.sysinfosystem

    def SysInfoToTable(self,sysinfosystem):
        rows = format_html_join(
            "",
            "<tr><td scope=\"row\">{}</td><td>{}</td></tr>",
            sysinfosystem.items(),
        )

        return format_html(
            '<div class="table-responsive">'
            '<table class="table">'
            '<thead><tr><th>items</th><th>value</th></tr></thead>'
            '<tbody>{}</tbody>'
            '</table>'
            '</div>',
            rows,
        )

