from django.conf import settings

def firma_context(request):
    return {
        'firma': settings.FIRMA_INFO
    }