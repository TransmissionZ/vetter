from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse
from .forms import AuthenticationForm
from datetime import datetime
from django.core.paginator import Paginator

# For login required @login_required(login_url='thenx:login')
def index(request):
    return redirect("thenx:login")



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('thenx:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'thenx/login.html', {'form':form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')


@login_required(login_url='thenx:login')
def dash_view(request):
    count = get_count_users() - 1
    return render(request, 'thenx/dashboard.html', {
        'count':count,
        'list':[1,2,3]})

def get_count_users():
    return User.objects.count()

@login_required(login_url='thenx:login')
def products_view(request):
    if request.method == "POST":
        urldata = request.POST.dict()
        url = urldata.get("url")
        dateadded = datetime.now().strftime("%d/%m/%Y %H:%M")
    list = [1,2,3,4,5,6,7,8,9,10,1,1,1,1,1,1,1]
    paginator = Paginator(list, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'thenx/products.html', {
        'count':2,
        'list':products})

@login_required(login_url='thenx:login')
def deleteurl(request, urlid = None):
    print(urlid)
    return redirect('thenx:products')