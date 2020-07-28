from django.urls import path

from . import views

from .forms import AuthenticationForm

app_name = 'thenx'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]