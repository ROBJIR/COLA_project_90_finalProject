from django.http.response import HttpResponse
from time import perf_counter
from datetime import timedelta
from django.shortcuts import render
from django.template.loader import render_to_string
from syscor.views.cfg import *
from syscor.views.tools import sysTools

# Provides page configuration, messages, and HTML table helpers.
# Poskytuje konfiguraci stránek, správu zpráv a pomocné nástroje pro tabulky HTML.
class WebMachine():
    web_page_attributes_template = {
        "application_code": "",
        "application_name": "",
        "application_module_start": "",
        "module_code": "",
        "module_name": "",
        "module_file_template": "",
        "application_file_menu": "",
    }
    web_page_data_template = {"htmlbody": ""}
    # Initializes the helper without instance data.
    # Inicializuje pomocnou třídu bez vlastních dat instance.
    def __init__(self):
        pass
    # Builds an HTML table from a list of dictionaries.
    # Vytváří tabulku HTML ze seznamu slovníků.
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

    # Renders dictionary keys and values in an HTML table.
    # Vykresluje klíče a hodnoty slovníku v tabulce HTML.
    @staticmethod
    def dictionary_to_html_table(data):
        """Render a flat dictionary as an escaped key/value HTML table."""
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        return WebMachine.html_table_generator(
            {"key": key, "value": value} for key, value in data.items()
        )

    # Uses the first record to choose columns for the HTML table.
    # Podle prvního záznamu určuje sloupce tabulky HTML.
    @staticmethod
    def html_table_generator(data):
        """Render dictionaries as a table using the first row's columns."""
        iterator = iter(data)
        first = next(iterator, None)
        columns = list(first.keys()) if first is not None else []

        # Yields cell values in column order.
        # Postupně vrací hodnoty buněk v pořadí sloupců.
        def rows():
            if first is not None:
                yield [first.get(column) for column in columns]
                for record in iterator:
                    yield [record.get(column) for column in columns]

        return render_to_string(
            "syscore/data-table.html",
            {"columns": columns, "rows": rows(), "has_records": first is not None},
        )

    # Returns the application configuration or one of its attributes.
    # Vrací konfiguraci aplikace nebo jeden její atribut.
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

    # Returns the module configuration or one of its attributes.
    # Vrací konfiguraci modulu nebo jeden jeho atribut.
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

    # Queues an alert in the session.
    # Přidává upozornění do fronty v relaci.
    @staticmethod
    def web_message_set(request, message_body = None,
                        message_alert = 'secondary', message_type = 'web' ):

        # Bootstrap alert Categories:
        # .alert-success, .alert-info, .alert-warning, .alert-danger
        # .alert-primary, .alert-secondary, .alert-light or .alert-dark

        message_alert = 'alert-' + message_alert.lower()
        message_type = message_type.lower()
        if message_type not in ['web', 'auth']:
            message_type = 'web'

        sys_msg_value = request.session.get(message_type) or []
        sys_msg_value.append({'message_alert':message_alert, 'message_body': message_body})
        request.session[message_type] = sys_msg_value

        return sys_msg_value

    # Reads and clears queued messages of the requested type.
    # Načítá a odstraňuje čekající zprávy požadovaného typu.
    @staticmethod
    def web_message_get(request, message_type = 'web_message'):

        sys_msg_value = request.session.get(message_type)
        sysTools.session_clear(request, message_type)
        # session clear
        request.session.pop(message_type, None)

        return sys_msg_value

    # Renders a configured page and records preparation and rendering times.
    # Vykresluje nakonfigurovanou stránku a zaznamenává dobu přípravy a vykreslení.
    def web_renderer (self, request, module_code = 'cassiopeia', web_data = None, web_message = None, auth_message = None):
        from syslog.views import WebLogging, SysLogging

        web_page_attrib = WebMachine.web_page_attributes_template.copy()
        web_page_attrib.update(WebMachine.web_application_module_attribute_get(module_code))
        web_page_attrib.update(WebMachine.web_application_attribute_get(web_page_attrib['application_code']))

        web_page_data = WebMachine.web_page_data_template.copy()
        web_page_data.update(web_data or {})

        web_sys_msg = WebMachine.web_message_get(request,'web') or []
        if web_message is not None:
            web_sys_msg.append(web_message)

        web_auth_msg = WebMachine.web_message_get(request,'auth') or []
        if auth_message is not None:
            web_auth_msg.append(auth_message)

        timedelta_content_prepare = timedelta(
            seconds=perf_counter() - request.preparation_started_at
        )
        web_render_start_time = perf_counter()

        response = render(request, web_page_attrib["module_file_template"]
                      , context = {  "web_page_attributes": web_page_attrib
                                    ,"web_message": web_sys_msg
                                    ,"auth_message": web_auth_msg
                                    ,"web_data": web_page_data  }
                      )

        timedelta_render_page = timedelta(seconds=perf_counter() - web_render_start_time)
        WebLogging.log(request, web_page_attrib["module_code"], web_page_attrib["module_file_template"], web_page_attrib, timedelta_render_page, timedelta_content_prepare )

        return response

# Adds shared page rendering to class-based views.
# Přidává společné vykreslování stránek do třídních pohledů.
class WebRenderMixin:
    # Renders the configured template with page data and records timing.
    # Vykresluje nastavenou šablonu s daty stránky a zaznamenává dobu zpracování.
    def page_render(
        self, request, module_code="cassiopeia", web_data=None,
        web_message=None, auth_message=None,):

        from syslog.views import WebLogging

        page_attributes = WebMachine.web_page_attributes_template.copy()
        page_attributes.update(WebMachine.web_application_module_attribute_get(module_code))
        page_attributes.update(
            WebMachine.web_application_attribute_get(page_attributes["application_code"])
        )

        page_data = WebMachine.web_page_data_template.copy()
        page_data.update(web_data or {})

        web_messages = WebMachine.web_message_get(request, "web") or []
        if web_message is not None:
            web_messages.append(web_message)

        auth_messages = WebMachine.web_message_get(request, "auth") or []
        if auth_message is not None:
            auth_messages.append(auth_message)

        preparation_duration = timedelta(seconds=perf_counter() - request.preparation_started_at)
        render_started_at = perf_counter()
        template_name = page_attributes["module_file_template"]
        response = render(request, template_name, context={
            "web_page_attributes": page_attributes,
            "web_message": web_messages,
            "auth_message": auth_messages,
            "web_data": page_data,
        })
        render_duration = timedelta(seconds=perf_counter() - render_started_at)
        WebLogging.log(
            request, page_attributes["module_code"], template_name, page_attributes,
            render_duration, preparation_duration,
        )
        return response