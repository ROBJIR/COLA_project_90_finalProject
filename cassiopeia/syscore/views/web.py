from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from syscore.views.tools import sysTools

class WebMachine():
    web_page_attributes_template = {
        "application_code": "cassiopeia",
        "application_name": "Cassiopeia Projects",
        "module_code": "cassiopeia",
        "module_template": "core-main.html",
        "module_name": "Cassiopeia Project",
    }
    web_page_data_template = {"htmlbody": ""}
    def __init__(self):
        pass
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

    # Bootstrap alert Categories:
    # .alert-success, .alert-info, .alert-warning, .alert-danger
    # .alert-primary, .alert-secondary, .alert-light or .alert-dark
    @staticmethod
    def web_message_set(request, message_body = None,
                        message_alert = 'alert-secondary', message_type = 'sys_message' ):

        message_type = message_type.lower()
        if message_type not in ['sys_message', 'auth_message']:
            message_type = 'sys_message'

        sys_msg_value = request.session.get(message_type) or []
        sys_msg_value.append({'message_alert':message_alert, 'message_body': message_body})
        request.session[message_type] = sys_msg_value

        return sys_msg_value

    @staticmethod
    def web_message_get(request, message_type = 'sys_message'):

        sys_msg_value = request.session.get(message_type)
        sysTools.session_clear(request, message_type)
        # session clear
        request.session.pop(message_type, None)

        return sys_msg_value

    def web_renderer (self, request, web_page_attributes = None, web_data = None, web_sys_message = None, web_auth_message = None):
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
        web_page_attrib = WebMachine.web_page_attributes_template.copy()
        web_page_attrib.update(web_page_attributes or {})

        web_page_data = WebMachine.web_page_data_template.copy()
        web_page_data.update(web_data or {})

        web_sys_msg = WebMachine.web_message_get(request,'sys_message') or []
        if web_sys_message is not None:
            web_sys_msg.append(web_sys_message)

        web_auth_msg = WebMachine.web_message_get(request,'auth_message') or []
        if web_auth_message is not None:
            web_auth_msg.append(web_auth_message)

        """
        print('=== WebMachine / web_render =================')
        print('--- web_page_attributes -----------------------')
        print(web_page_attrib)
        print('--- web_data ---------------------------------')
        print(web_page_data)
        print('--- web_sys_message ---------------------------------')
        print(web_sys_msg)
        print('--- web_auth_message ---------------------------------')
        print(web_auth_msg)
        # for key, value in webdata.items():
        #    print (key, value)
        print('==============================================')
        """


        return render(request, web_page_attributes["module_template"]
                      , context = {  "web_page_attributes": web_page_attrib
                                    ,"web_sys_message": web_sys_msg
                                    ,"web_auth_message": web_auth_msg
                                    ,"web_data": web_page_data  }
                      )

