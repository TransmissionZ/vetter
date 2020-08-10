from django.urls import path

from . import views

from .forms import AuthenticationForm

app_name = 'thenx'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dash_view, name='dashboard'),
    path('dashboard/products/', views.products_view, name='products'),
    path('dashboard/products/delete/(<urlid>)/', views.deleteurl, name='deleteurl'),
]