class ClientIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if str_lista_ip:
            ip = str_lista_ip.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        request.client_ip = ip
        response = self.get_response(request)
        return response