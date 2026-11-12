import datetime
from django.shortcuts import render
from django.http import HttpResponse
import random
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Produs, Categorie
from django.http import HttpResponse
from django.core.mail import send_mail

ZILE_ROMANIA = ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']
LUNI_ROMANIA = ['', 'Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie', 'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie']

TOATE_ACCESARILE = []

class Accesare:
    _id_counter = 1

    def __init__(self, request):
        self.id = Accesare._id_counter
        Accesare._id_counter += 1
        self.ip_client = self.get_ip(request)
        self.url = request.build_absolute_uri()
        self.path = request.path
        self.parametri = request.GET
        self.data = datetime.datetime.now()
        
        TOATE_ACCESARILE.append(self)

    def get_ip(self, request):
        str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if str_lista_ip:
            return str_lista_ip.split(',')[-1].strip()
        else:
            return request.META.get('REMOTE_ADDR')

    def lista_parametri(self):
        if not self.parametri:
            return []
        rezultat = []
        for key in self.parametri.keys():
            val = self.parametri.get(key)
            rezultat.append((key, val if val is not None else None))
        return rezultat

    def string_url(self):
        return self.url

    def pagina(self):
        return self.path

    def calculeaza_data(self, format_tip=""):
        zi_sapt = ZILE_ROMANIA[self.data.weekday()]
        zi_luna = self.data.day
        nume_luna = LUNI_ROMANIA[self.data.month]
        an = self.data.year
        
        data_formatata = f"{zi_sapt}, {zi_luna} {nume_luna} {an}"
        timp_formatat = self.data.strftime("%H:%M:%S")

        if format_tip == "zi":
            return data_formatata
        elif format_tip == "timp":
            return timp_formatat
        else:
            return data_formatata

    def __str__(self):
        return (f"id: {self.id} | ip_client: {self.ip_client} | url: {self.string_url()} | "
                f"pagina: {self.pagina()} | data: {self.calculeaza_data()} | "
                f"lista_parametri: {self.lista_parametri()}")

def index(request):
    acc = Accesare(request)
    print(acc)
    
    return render(request, 'trading_app/index.html')


def info_view(request):
    acc = Accesare(request)
    print(acc) 

    # Preluare parametru 'data' din query string (ex: ?data=zi sau ?data=timp)
    tip_param = request.GET.get('data', '')
    text_data_ora = acc.calculeaza_data(tip_param)

    html_content = f"""
    <html>
        <head>
            <title>Informații despre server</title>
        </head>
        <body>
            <h1>Informații despre server</h1>
            <section>
                <h2>Data și ora</h2>
                <p>{text_data_ora}</p>
            </section>
        </body>
    </html>
    """
    return HttpResponse(html_content)

def log_view(request):
    acc = Accesare(request)
    
    # 1. Parametrul 'ultimele'
    ultimele_param = request.GET.get('ultimele')
    accesari_afisate = TOATE_ACCESARILE
    eroare_ultimele = ""
    
    if ultimele_param is not None:
        try:
            n = int(ultimele_param)
            k = len(TOATE_ACCESARILE)
            if n > k:
                eroare_ultimele = f"Exista doar {k} accesari fata de {n} accesari cerute."
                accesari_afisate = TOATE_ACCESARILE
            else:
                accesari_afisate = TOATE_ACCESARILE[-n:]
        except ValueError:
            return HttpResponse("Eroare: Parametrul 'ultimele' trebuie sa fie o valoare numerica intreaga!")

    # 2. Parametrul 'iduri' si 'dubluri'
    iduri_params = request.GET.getlist('iduri')
    dubluri = request.GET.get('dubluri', 'false').lower() == 'true'
    
    if iduri_params:
        ids_cautate = []
        for grup in iduri_params:
            for s_id in grup.split(','):
                if s_id.strip().isdigit():
                    ids_cautate.append(int(s_id.strip()))
        
        if not dubluri:
            # Eliminam duplicatele pastrand ordinea
            ids_cautate = list(dict.fromkeys(ids_cautate))
            
        accesari_afisate = [a for a in TOATE_ACCESARILE if a.id in ids_cautate]
        # Sortam in ordinea ceruta de utilizator in query string
        accesari_afisate.sort(key=lambda x: ids_cautate.index(x.id))

    # 3. Parametrul 'accesari'
    accesari_val = request.GET.get('accesari')
    html_suplimentar_accesari = ""
    if accesari_val == "nr":
        html_suplimentar_accesari = f"<p>Număr total de accesări în sesiunea curentă: {len(TOATE_ACCESARILE)}</p>"
    elif accesari_val == "detalii":
        lista_li = "".join([f"<li>Data și ora: {a.calculeaza_data()}</li>" for a in accesari_afisate])
        html_suplimentar_accesari = f"<ul>{lista_li}</ul>"

    # 4. Sectiunea "Parametri"
    numar_parametri = len(request.GET)
    nume_parametri = list(request.GET.keys())
    sectiune_parametri = f"<h3>Parametri primiți ({numar_parametri}):</h3><p>{nume_parametri}</p>"

    # 5. Parametrul 'tabel'
    tabel_param = request.GET.get('tabel')
    html_tabel = ""
    if tabel_param is not None:
        if tabel_param == "tot":
            coloane = ['id', 'ip_client', 'string_url', 'pagina', 'calculeaza_data']
        else:
            coloane = [c.strip() for c in tabel_param.split(',')]
            
        th_s = "".join([f"<th>{col}</th>" for col in coloane])
        tr_s = ""
        for a in accesari_afisate:
            tds = ""
            for col in coloane:
                val = getattr(a, col, "")
                if callable(val):
                    val = val()
                tds += f"<td>{val}</td>"
            tr_s += f"<tr>{tds}</tr>"
        html_tabel = f"<table border='1'><tr>{th_s}</tr>{tr_s}</table>"

    # 6. Cea mai putin si cea mai mult accesata pagina
    pagini_numar = {}
    for a in TOATE_ACCESARILE:
        p = a.pagina()
        pagini_numar[p] = pagini_numar.get(p, 0) + 1
        
    cel_mai_mult, cel_mai_putin = "", ""
    if pagini_numar:
        cel_mai_mult = max(pagini_numar, key=pagini_numar.get)
        cel_mai_putin = min(pagini_numar, key=pagini_numar.get)

    statistici_pagini = f"<p>Pagina cea mai accesată: <b>{cel_mai_mult}</b> | Pagina cea mai puțin accesată: <b>{cel_mai_putin}</b></p>"

    # Construire raspuns final
    continut = f"<h1>Pagina de Log</h1>{sectiune_parametri}{html_suplimentar_accesari}"
    if eroare_ultimele:
        continut += f"<p style='color:red;'>{eroare_ultimele}</p>"
    if html_tabel:
        continut += html_tabel
    else:
        # Afisare lista simpla daca nu e tabel
        ul_acc = "".join([f"<li>{str(a)}</li>" for a in accesari_afisate])
        continut += f"<ul>{ul_acc}</ul>"
        
    continut += statistici_pagini
    return HttpResponse(continut)


def detaliu_accesare(request, id_accesare):
    acc = Accesare(request)
    gasit = next((a for a in TOATE_ACCESARILE if a.id == int(id_accesare)), None)
    if not gasit:
        return HttpResponse("Accesarea nu a fost găsită.", status=404)
    return HttpResponse(f"<h1>Detalii Accesare #{gasit.id}</h1><p>{str(gasit)}</p>")

def lista_produse(request, nume_categorie=None):
    categorie_curenta = None
    produse = Produs.objects.select_related('categorie').all()

    # Filtrare după categorie dacă suntem pe ruta /categorii/<nume_categorie>/
    if nume_categorie:
        categorie_curenta = get_object_or_404(Categorie, nume=nume_categorie)
        produse = produse.filter(categorie=categorie_curenta)

    # 1. Filtrare cumulativă după taguri active (?tag=holo&tag=rar)
    taguri_active = request.GET.getlist('tag')
    for tag in taguri_active:
        produse = produse.filter(tags__contains=[tag])

    # 2. Sortare (?sort=a|d&col=pret|titlu|stoc)
    sort_dir = request.GET.get('sort', '')
    sort_col = request.GET.get('col', 'titlu')
    coloane_permise = {'titlu', 'pret', 'stoc', 'data_adaugare'}

    if sort_dir in ('a', 'd') and sort_col in coloane_permise:
        prefix = '' if sort_dir == 'a' else '-'
        produse = produse.order_by(f'{prefix}{sort_col}')

    # 3. Paginare pe produsele deja filtrate și sortate
    paginator = Paginator(produse, settings.PROD_PER_PAG)
    numar_pagina = request.GET.get('page', 1)
    page_obj = paginator.get_page(numar_pagina)

    # Construim query string-ul fără parametrul 'page' pentru linkurile de paginare
    params_fara_page = request.GET.copy()
    params_fara_page.pop('page', None)
    query_string_paginare = params_fara_page.urlencode()

    context = {
        'page_obj': page_obj,
        'categorie_curenta': categorie_curenta,
        'taguri_active': taguri_active,
        'sort_dir': sort_dir,
        'sort_col': sort_col,
        'stoc_min': settings.STOC_MIN,
        'query_string_paginare': query_string_paginare,
    }
    return render(request, 'trading_app/produse.html', context)


def produse_categorie(request, nume_categorie):
    return lista_produse(request, nume_categorie=nume_categorie)


def detaliu_produs(request, produs_id):
    # Afișează 404 (pagină de eroare) dacă produsul nu există
    produs = get_object_or_404(Produs, id=produs_id)

    # Selectare aleatoare a K produse din aceeași categorie
    produse_aceeasi_cat = list(
        Produs.objects.filter(categorie=produs.categorie).exclude(id=produs.id)
    )
    k = min(len(produse_aceeasi_cat), settings.NR_PRODUSE_SIMILARE)
    produse_similare = random.sample(produse_aceeasi_cat, k)

    return render(request, 'trading_app/detaliu_produs.html', {
        'produs': produs,
        'produse_similare': produse_similare,
        'stoc_min': settings.STOC_MIN,
    })

def produse_view(request):
    return render(request, 'trading_app/in_lucru.html')

def contact_view(request):
    return render(request, 'trading_app/in_lucru.html')

def cos_virtual_view(request):
    return render(request, 'trading_app/in_lucru.html')

def istoric_view(request):
    return render(request, 'trading_app/in_lucru.html')

def despre_view(request):
    return render(request, 'trading_app/despre.html')

def trimite_email_test(request):
    send_mail(
        subject='Bun venit la Magazinul TCG!',
        message='Salut! Acesta este un mesaj text simplu trimis din Django.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['razvytheawesomeunicorn@gmail.com'],
        html_message='<h2>Bun venit la Magazinul TCG!</h2><p>Comanda sau contul tău a fost înregistrat cu succes.</p>',
        fail_silently=False,
    )
    return HttpResponse("E-mailul a fost trimis cu succes!")
