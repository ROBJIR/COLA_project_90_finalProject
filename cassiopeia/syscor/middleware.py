from time import perf_counter

# Records when Django starts processing each request.
# Zaznamenává začátek zpracování každého požadavku v Django.
class SyscorTimingMiddleware:
    # Stores the next callable in the middleware chain.
    # Ukládá další volatelný objekt v řetězci middleware.
    def __init__(self, get_response):
        self.get_response = get_response
    # Sets the start timestamp and forwards the request.
    # Nastavuje čas zahájení a předává požadavek dál.
    def __call__(self, request):
        request.preparation_started_at = perf_counter()
        response = self.get_response(request)
        duration_seconds = (
            perf_counter() - request.preparation_started_at
        )
        return response