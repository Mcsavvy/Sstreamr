class AjaxRequest:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'x-ajax' in request.headers:
            request.isAjax = True
        else:
            if request.method == "GET":
                request.isAjax = ("x-ajax" in request.GET)
            elif request.method == "POST":
                request.isAjax = ("x-ajax" in request.POST)
        return self.get_response(request)
