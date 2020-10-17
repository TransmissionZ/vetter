from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .forms import AuthenticationForm

app_name = 'thenx'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dash_view, name='dashboard'),
    path('dashboard/products/', views.products_view, name='products'),
    path('dashboard/products/<str:sku>', views.redirecttoproduct, name='specificproduct'),
    path('dashboard/products/delete/(<urlid>)/(<pid>)', views.deleteurl, name='deleteurl'),
    path('dashboard/products/setimp', views.set_imp, name='setimp'),
    path('dashboard/rules/parser', views.rules_parser, name='parserrules'),
    path('dashboard/rules/pricelist', views.rules_price_list, name='pricelistrules'),
    path('dashboard/rules/margins', views.rules_margins, name='marginsrules'),
    path('dashboard/rules/vat', views.rules_vat, name='vatrules'),
    path('dashboard/rules/warranty', views.rules_warranty, name='warrantyrules'),
    path('dashboard/rules/', views.rules_view, name='rules'),
    path('rules/getDetails/', views.getDetails, name='details'),
    path('validatesku/', views.validateSKU, name='validatesku'),
    path('dashboard/rules/delete/(<ruleid>)/(<rule>)', views.deleterule, name='deleterule'),
    path('dashboard/products/uploadcompetitors/', views.competitors_upload, name='uploadcomp')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)