from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from syscore.views.tools import sysTools

class WebMachine():
    def __init__(self):
        self.webpageattributes = {
              "application_code":   "cassiopeia"
            , "application_name":   "Cassiopeia Projects"
            , "module_code":        "cassiopeia"
            , "module_template":    "core-main.html"
            , "module_name":        "Cassiopeia Project"}
        self.webdata = {"htmlbody":""}
    def table_list_genertor(self, data):
        if len(data) == 0:
            self.message_detail  = self.html_message_set("data was not loaded", "warning")
            return ""
        htmlcode = f'<table class="table">\n'
        htmlcode = f"{htmlcode}  <tr>\n"
        for tabheader in data[0].keys():
            htmlcode = f"{htmlcode}    <th>{tabheader}</th>\n"
        htmlcode = f"{htmlcode}  </tr>\n"

        for row in data:
            htmlcode = f"{htmlcode}  <tr>\n"
            for ikey, ivalue in row.items():
                htmlcode = f"{htmlcode}    <td>{ivalue}</td>\n"

            htmlcode = f"{htmlcode}  </tr>\n"

        htmlcode = f"{htmlcode}</table>\n"
        return htmlcode

    @staticmethod
    def dictionary_to_html_table(data):
        """Render a flat dictionary as an escaped key/value HTML table."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        return WebMachine.html_table_generator(
            {"key": key, "value": value} for key, value in data.items()
        )

    @staticmethod
    def html_table_generator(data):
        """Render dictionaries as a table using the first row's columns."""
        iterator = iter(data)
        first = next(iterator, None)
        columns = list(first.keys()) if first is not None else []

        def rows():
            if first is not None:
                yield [first.get(column) for column in columns]
                for record in iterator:
                    yield [record.get(column) for column in columns]

        return render_to_string(
            "syscore/data-table.html",
            {"columns": columns, "rows": rows(), "has_records": first is not None},
        )
    @staticmethod
    def web_message_generator(webmessage = None):
        wmsg = {
            "message_type": "standard",
            "message_alert": "alert-dark", # .alert-success, .alert-info, .alert-warning, .alert-danger, .alert-primary, .alert-secondary, .alert-light or .alert-dark
            "message_header": "",
            "message_body": "",
            "message_html": "",
        }

        if webmessage is not None:
            wmsg.update(webmessage)

        if not wmsg["message_html"] and wmsg["message_body"]:
            wmsg["message_html"] = (f' \
                <div class="row mt-3"> \
                    <div class="col-12 col-lg-4"></div> \
                    <div class="col-12 col-lg-4"> \
                        <div class ="alert {wmsg["message_alert"]} alert-dismissible"> \
                            <button type = "button" class ="btn-close" data-bs-dismiss="alert"></button> \
                                {wmsg["message_body"]} \
                        </div> \
                    </div> \
                    <div class="col-12 col-lg-4"></div> \
                </div>')
        return wmsg

    @staticmethod
    def sys_message_set(request, message_alert, message_body):
        sysTools.session_set(request, 'sys_message',{'message_alert': message_alert, 'message_body': message_body})
        return sysTools.session_get(request, 'sys_message')
    @staticmethod
    def sys_message_get(request):
        sys_message_value = sysTools.session_get(request, 'sys_message')
        sysTools.session_clear(request, 'sys_message')
        return sys_message_value

    def web_renderer (self, request, webpageattributes = None, webdata = None, webmessage = None):
        """
        print('=== WebMachine / web_render =================')
        print('--- webpageattributes -----------------------')
        print(webpageattributes)
        print('--- webdata ---------------------------------')
        print(webdata)
        #for key, value in webdata.items():
        #    print (key, value)
        print('==============================================')
        """
        if webpageattributes is None:
            webpageattributes = self.webpageattributes.copy()

        if webdata is None:
            webdata = self.webdata.copy()

        if webmessage is None:
            webmessage = WebMachine.sys_message_get(request) or {}

        webmessage = WebMachine.web_message_generator(webmessage)

        return render(request, webpageattributes["module_template"]
                      , context={"WebPageAttributes": webpageattributes, "WebMessage": webmessage, "WebData": webdata})

