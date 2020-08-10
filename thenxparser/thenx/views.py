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
from .models import Product, Competitor_URL
from .tasks import UpdateDB
from django.db.models import Q, Count

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
        if request.user.is_authenticated:
            return redirect('thenx:dashboard')

    return render(request, 'thenx/login.html', {'form':form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')


@login_required(login_url='thenx:login')
def dash_view(request):
    totalp = Product.objects.count()
    totalc = Competitor_URL.objects.count()
    comp = Competitor_URL.objects.order_by('comp_name').distinct().count()
    UpdateDB()
    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    if request.method == 'GET':
        if 'q' in request.GET:
            query = request.GET.get('q')
            print(query)
            plist = Product.objects.filter(Q(SKU__icontains=query)|Q(name__icontains=query)|Q(brand__icontains=query))
        else:
            plist = Product.objects.all()

        if 'brand' in request.GET:
            query = request.GET.get('brand')
            if query != 'All' and query != None:
                plist = Product.objects.filter(Q(brand__icontains=query))
            else:
                plist = Product.objects.all()

    #UpdateDB()
    return render(request, 'thenx/dashboard.html', {
        'totalp':totalp,
        'totalc':totalc,
        'comp':comp,
        'list':plist,
        'brands':brands,})

def get_count_users():
    return User.objects.count()

@login_required(login_url='thenx:login')
def products_view(request):
    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    plist = Product.objects.all()
    if request.method == "POST":
        urldata = request.POST.dict()
        url = urldata.get("url")
        print(urldata)
        #dateadded = datetime.now().strftime("%d/%m/%Y %H:%M")
        queryflag = False
        if 'q' in request.GET:
            query = request.GET.get('q')
            if query != '':
                plist = Product.objects.filter(Q(SKU__icontains=query)|Q(name__icontains=query)|Q(brand__icontains=query))
                queryflag = True
            else:
                plist = Product.objects.all()

        if 'brand' in request.GET:
            bquery = request.GET.get('brand')
            if bquery != 'All' and bquery != None:
                if queryflag:
                    plist = Product.objects.filter((
                        Q(SKU__icontains=query) | Q(name__icontains=query) | Q(brand__icontains=query)) & (Q(brand__icontains=bquery)) )
                else:
                    plist = Product.objects.filter(Q(brand__icontains=bquery))

            else:
                if queryflag:
                    pass
                else:
                    plist = Product.objects.all()
    if request.method == "GET":
        queryflag = False
        if 'q' in request.GET:
            query = request.GET.get('q')
            if query != '':
                plist = Product.objects.filter(
                    Q(SKU__icontains=query) | Q(name__icontains=query) | Q(brand__icontains=query))
                queryflag = True
            else:
                plist = Product.objects.all()

        if 'brand' in request.GET:
            bquery = request.GET.get('brand')
            if bquery != 'All' and bquery != None:
                if queryflag:
                    plist = Product.objects.filter((
                                                           Q(SKU__icontains=query) | Q(name__icontains=query) | Q(
                                                       brand__icontains=query)) & (Q(brand__icontains=bquery)))
                else:
                    plist = Product.objects.filter(Q(brand__icontains=bquery))

            else:
                if queryflag:
                    pass
                else:
                    plist = Product.objects.all()

    paginator = Paginator(plist, 50)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'thenx/products.html', {
        'list':products,
        'brands':brands,})

@login_required(login_url='thenx:login')
def deleteurl(request, urlid = None):
    print(urlid)
    return redirect('thenx:products')

