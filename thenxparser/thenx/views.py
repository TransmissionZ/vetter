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
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from datetime import timedelta
import json
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
    comp = Competitor_URL.objects.order_by('comp_name').values_list("comp_name", flat=True).distinct().count()

    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    delta = datetime.now() - timedelta(days=1)
    recentlychanged = Product.objects.filter(dateupdated__gte=delta).count()
    print(recentlychanged)
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
        'brands':brands,
        'recentlychanged':recentlychanged})

def get_count_users():
    return User.objects.count()

@login_required(login_url='thenx:login')
def products_view(request):
    #UpdateDB()
    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    plist = Product.objects.all()
    if request.method == "POST":
        urldata = request.POST.dict()
        url = urldata.get("url")
        p = urldata.get("product")
        p = Product.objects.filter(SKU=p).first()
        if p.competitor_url_set.filter(url=url).count() == 0:
            c = p.competitor_url_set.create(url=url)
            c.scrap()
        else:
            messages.error(request, "This URL Already Exists")
        print(p.competitor_url_set.all())
        #dateadded = datetime.now().strftime("%d/%m/%Y %H:%M")
        queryflag1 = False
        queryflag2 = False
        if 'q' in request.GET:
            query = request.GET.get('q')
            queryflag1 = True
        else:
            query = ''

        if 'brand' in request.GET:
            bquery = request.GET.get('brand')
            queryflag2 = True
        else:
            bquery = 'All'

        if queryflag1 or queryflag2:
            return HttpResponseRedirect('./' + '?brand=' + str(bquery) + '&' + 'q=' + str(query))
        else:
            return redirect('thenx:products')

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
    Competitor_URL.objects.filter(pk=urlid).delete()
    dict = request.POST.dict()
    if 'brand' in request.POST and 'q' in request.POST:
        return HttpResponseRedirect(reverse('thenx:products') + "?brand=" + dict.get('brand') + "&q=" + dict.get('q'))
    return redirect('thenx:products')

@login_required()
def set_imp(request):
    sku = None
    if request.method == "GET":
        sku = request.GET.get('pk')
        chk = request.GET.get('chk')

    if sku and chk:
        ob = Product.objects.filter(SKU__exact=sku).first()
        ob.important = chk
        ob.save()

    return redirect('thenx:products')

def redirecttoproduct(request, sku):
    return HttpResponseRedirect('./' + '?brand=All' + '&' + 'q=' + sku)

@login_required(login_url='thenx:login')
def rules_view(request):
    totalcomps = [_ for _ in range(Competitor_URL.objects.order_by('comp_name').values_list("comp_name", flat=True).distinct().count())]
    return render(request, 'thenx/rules.html', {'totalcomps':totalcomps})

def rules_parser(request):

    return render(request, 'thenx/rules_parser.html', )

def rules_price_list(request):

    return render(request, 'thenx/rules_pricelist.html', )

def rules_margins(request):

    return render(request, 'thenx/rules_margin.html', )

def rules_vat(request):

    return render(request, 'thenx/rules_vat.html', )

def rules_warranty(request):

    return render(request, 'thenx/rules_warranty.html', )

def getDetails(request):
    choice = request.GET.get('choice', '')
    if choice == 'cat':
        all_cats = Product.objects.order_by('category').values_list("category", flat=True).distinct()
        result_set = list(set(x for l in all_cats for x in l))
    elif choice == 'sup':
        result_set = list(Product.objects.order_by('supplier').values_list("supplier", flat=True).distinct())
    else:
        result_set = []
    return HttpResponse(json.dumps(result_set), content_type='application/json')