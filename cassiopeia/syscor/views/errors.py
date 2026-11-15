from syscor.views.web import WebMachine

def page_not_found(request, exception):
    response = WebMachine().web_renderer(request, "404")
    response.status_code = 404
    return response
