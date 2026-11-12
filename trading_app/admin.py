from django.contrib import admin
from .models import Categorie, SetColectie, Produs, Producator, RevistaPromotionala, Ambalaj

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nume',)}

admin.site.register(SetColectie)
admin.site.register(Produs)
admin.site.register(Producator)
admin.site.register(RevistaPromotionala)
admin.site.register(Ambalaj)