from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info_view, name='info'),
    path('log', views.log_view, name='log'),
    path('produse', views.produse_view, name='produse'),
    path('produse/', views.lista_produse, name='lista_produse'),
    path('produse/<int:produs_id>/', views.detaliu_produs, name='detaliu_produs'),
    path('categorii/<str:nume_categorie>/', views.produse_categorie, name='produse_categorie'),
    path('contact', views.contact_view, name='contact'),
    path('cos_virtual', views.cos_virtual_view, name='cos_virtual'),
    path('istoric', views.istoric_view, name='istoric'),
    path('despre', views.despre_view, name='despre'),
    path('trimite-mail/', views.trimite_email_test, name='trimite_email_test'),
    re_path(r'^accesare(?P<id_accesare>\d+)$', views.detaliu_accesare, name='detaliu_accesare'),
]