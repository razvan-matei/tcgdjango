import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Categorie, SetColectie, Produs, Producator, RevistaPromotionala, Ambalaj

# Personalizare titluri și buton "View site"
admin.site.site_title = "Administrare TCG Shop"
admin.site.site_header = "Panou de Control - Magazin Trading Cards"
admin.site.index_title = "Gestiune Magazin TCG"
admin.site.site_url = "/"  # Redirecționează "View site" către pagina principală a magazinului


@admin.action(description="Exportă produsele selectate în format CSV")
def exporta_produse_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="produse_tcg.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Titlu', 'Categorie', 'Preț', 'Stoc', 'Stare'])
    for p in queryset:
        writer.writerow([p.id, p.titlu, p.categorie.nume, p.pret, p.stoc, p.stare])
    return response


@admin.action(description="Marchează produsele selectate ca 'Foarte rar' (preț min 50 RON)")
def marcheaza_foarte_rar(modeladmin, request, queryset):
    for p in queryset:
        p.este_foarte_rar = True
        if p.pret < 50:
            p.pret = 50.00
        p.save()


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    # Ordine custom a coloanelor + câmp din entitatea legată (categorie__nume)
    list_display = ('titlu', 'categorie', 'afisare_pret_colorat', 'stoc', 'stare', 'este_foarte_rar')
    list_filter = ('categorie', 'stare', 'este_foarte_rar')
    search_fields = ('titlu', 'categorie__nume')
    search_help_text = "Caută produse după titlu sau după numele categoriei."
    ordering = ('-pret',)  # Ordonare descrescătoare după preț
    list_per_page = 5       # Maxim 5 itemuri pe pagină
    actions = [exporta_produse_csv, marcheaza_foarte_rar]

    # Împărțire în 2 secțiuni, a doua fiind colapsabilă doar cu câmpuri opționale
    fieldsets = (
        ('Informații Obligatorii & Principale', {
            'fields': ('titlu', 'categorie', 'pret', 'stoc', 'stare', 'este_foarte_rar')
        }),
        ('Detalii Opționale & Colecție', {
            'classes': ('collapse',),
            'fields': ('imagine', 'seturi', 'data_lansare', 'tags'),
        }),
    )

    @admin.display(description="Preț (RON)", ordering="pret")
    def afisare_pret_colorat(self, obj):
        culoare = "#c0392b" if obj.este_foarte_rar else "#27ae60"
        return format_html('<strong style="color: {};">{} RON</strong>', culoare, obj.pret)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nume', 'slug', 'afisare_culoare', 'popularitate')
    prepopulated_fields = {'slug': ('nume',)}
    search_fields = ('nume', 'descriere')
    search_help_text = "Caută categorii după nume sau cuvinte din descriere."

    @admin.display(description="Culoare Tematică")
    def afisare_culoare(self, obj):
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 4px;"><i>{}</i></span>',
            obj.culoare, obj.culoare
        )


@admin.register(SetColectie)
class SetColectieAdmin(admin.ModelAdmin):
    list_display = ('nume_set', 'an_aparitie')
    search_fields = ('nume_set', 'an_aparitie')
    search_help_text = "Caută seturi după denumirea setului sau anul apariției."


@admin.register(Producator)
class ProducatorAdmin(admin.ModelAdmin):
    list_display = ('nume_companie', 'tara_origine', 'website')
    search_fields = ('nume_companie', 'tara_origine')
    search_help_text = "Caută producători după numele companiei sau țara de origine."


@admin.register(RevistaPromotionala)
class RevistaPromotionalaAdmin(admin.ModelAdmin):
    # Afișează și țara producătorului legat prin ForeignKey
    list_display = ('titlu_revista', 'editie_numar', 'producator', 'tara_producator')
    search_fields = ('titlu_revista', 'producator__nume_companie')
    search_help_text = "Caută reviste după titlu sau după numele producătorului."

    @admin.display(description="Țara Producătorului")
    def tara_producator(self, obj):
        return obj.producator.tara_origine


@admin.register(Ambalaj)
class AmbalajAdmin(admin.ModelAdmin):
    list_display = ('tip_ambalaj', 'greutate_gr')
    search_fields = ('tip_ambalaj', 'greutate_gr')
    search_help_text = "Caută ambalaje după tip sau greutate."