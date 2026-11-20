from syscor.views.web import WebRenderMixin

# Renders the custom page not found response with status 404.
# Vykresluje vlastní stránku pro nenalezený obsah se stavem 404.
def page_not_found(request, exception):
    response = WebRenderMixin().page_render(request, "404")
    response.status_code = 404
    return response
