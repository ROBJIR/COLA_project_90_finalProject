from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html, format_html_join

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

    def html_table_generator(data):
        iterator = iter(data)
        first = next(iterator, None)

        if first is None:
            return format_html("<p>{}</p>", "no records!")

        columns = list(first.keys())

        header = format_html_join(
            "",
            '<th scope="col">{}</th>',
            ((column,) for column in columns),
        )
        def create_row(record):
            cells = format_html_join(
                "",
                "<td>{}</td>",
                (
                    ("" if record.get(column) is None else record[column],)
                    for column in columns
                ),
            )
            return format_html("<tr>{}</tr>", cells)
        def rows():
            yield (create_row(first),)
            for record in iterator:
                yield (create_row(record),)
        body = format_html_join("", "{}", rows())

        return format_html(
            """
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead><tr>{}</tr></thead>
                    <tbody>{}</tbody>
                </table>
            </div>
            """,
            header,
            body,
        )
    def web_message_generator(self, webmessage = None ):
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
            wmsg["message_html"] = f' \
<div class ="alert {wmsg["message_alert"]} alert-dismissible"> \
    <button type = "button" class ="btn-close" data-bs-dismiss="alert"> </button> \
        {wmsg["message_body"]} \
</div>'
        return wmsg

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
            webmessage = {}
        else:
            webmessage = WebMachine.web_message_generator(self, webmessage)

        # ebmessage = self.web_message_generator(webmessage)
        return render(request, webpageattributes["module_template"]
                      , context={"WebPageAttributes": webpageattributes, "WebMessage": webmessage, "WebData": webdata})
