from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from syscor.views.cfg import *
from syscor.views.tools import sysTools

class WebMachine():
    web_page_attributes_template = {
        "application_code": "",
        "application_name": "",
        "module_code": "",
        "module_name": "",
        "module_file_template": "",
        "application_file_menu": "",
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

    # Get Application Attributes for WEB_RENDER
    @staticmethod
    def web_application_attribute_get(application_code: str = 'cassiopeia', application_attribut: str = None) -> dict[str, str] | str:
        application_code = application_code.lower()
        attribs = WEB_APPLICATIONS[application_code].copy()
        attribs['application_code'] = application_code

        if application_attribut is None:
            return attribs
        else:
            application_attribut = application_attribut.lower()
            return attribs[application_attribut]

    # Get Module Attributes for WEB_RENDER
    @staticmethod
    def web_application_module_attribute_get(module_code: str = 'cassiopeia', module_attribut: str = None) -> dict[str, str] | str:
        module_code = module_code.lower()
        attribs = WEB_APPLICATION_MODULES[module_code].copy()
        attribs['module_code'] = module_code

        if module_attribut is None:
            return attribs
        else:
            module_attribut = module_attribut.lower()
            return attribs[module_attribut]

    # Bootstrap alert Categories:
    # .alert-success, .alert-info, .alert-warning, .alert-danger
    # .alert-primary, .alert-secondary, .alert-light or .alert-dark
    @staticmethod
    def web_message_set(request, message_body = None,
                        message_alert = 'alert-secondary', message_type = 'web_message' ):

        message_type = message_type.lower()
        if message_type not in ['web_message', 'auth_message']:
            message_type = 'web_message'

        sys_msg_value = request.session.get(message_type) or []
        sys_msg_value.append({'message_alert':message_alert, 'message_body': message_body})
        request.session[message_type] = sys_msg_value

        return sys_msg_value

    @staticmethod
    def web_message_get(request, message_type = 'web_message'):

        sys_msg_value = request.session.get(message_type)
        sysTools.session_clear(request, message_type)
        # session clear
        request.session.pop(message_type, None)

        return sys_msg_value

    def web_renderer (self, request, module_code = 'cassiopeia', web_data = None, web_message = None, auth_message = None):
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
        web_page_attrib.update(WebMachine.web_application_module_attribute_get(module_code))
        web_page_attrib.update(WebMachine.web_application_attribute_get(web_page_attrib['application_code']))

        print (web_page_attrib)

        web_page_data = WebMachine.web_page_data_template.copy()
        web_page_data.update(web_data or {})

        web_sys_msg = WebMachine.web_message_get(request,'web_message') or []
        if web_message is not None:
            web_sys_msg.append(web_message)

        web_auth_msg = WebMachine.web_message_get(request,'auth_message') or []
        if auth_message is not None:
            web_auth_msg.append(auth_message)

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

        return render(request, web_page_attrib["module_file_template"]
                      , context = {  "web_page_attributes": web_page_attrib
                                    ,"web_message": web_sys_msg
                                    ,"auth_message": web_auth_msg
                                    ,"web_data": web_page_data  }
                      )

