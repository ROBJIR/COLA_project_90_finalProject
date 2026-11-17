from time import perf_counter

class SyscorTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        request.preparation_started_at = perf_counter()
        response = self.get_response(request)
        duration_seconds = (
            perf_counter() - request.preparation_started_at
        )
        return response