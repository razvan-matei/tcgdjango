from django.conf import settings
from django.db.models import Count
from .models import Categorie

def firma_context(request):
    return {
        'firma': settings.FIRMA_INFO
    }

def categorii_meniu(request):
    # Selectează doar categoriile care au minim 1 produs asociat
    categorii_active = Categorie.objects.annotate(nr_produse=Count('produse')).filter(nr_produse__gt=0)
    return {'categorii_meniu': categorii_active}