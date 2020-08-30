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
from .models import *
from .tasks import *
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
    testcelery.delay()
    return render(request, 'thenx/rules.html', {'totalcomps':totalcomps})

def rules_parser(request):
    if request.method == "POST":
        dict = request.POST.dict()
        priceshouldbe = dict["HL1"]
        than = dict["than1"]
        thantype = dict["thantype"]
        thanHL = dict["HL2"]
        competitor = dict["comp"]
        butnotlowerthan = dict["notlowerthan"]
        butnotlowerthantype = dict["notlowerthantype"]
        ob = competitorrules.objects.filter(competitor=competitor, priceshouldbe=priceshouldbe, thanHL=thanHL, butnotlowerthan=butnotlowerthan).first()
        if ob:
            ob.than = than
            ob.thantype = thantype
            ob.butnotlowerthantype = butnotlowerthantype
        else:
            ob = competitorrules.objects.create(priceshouldbe=priceshouldbe, than=than, thantype=thantype, thanHL=thanHL,
                                                competitor=competitor, butnotlowerthan=butnotlowerthan, butnotlowerthantype=butnotlowerthantype)
        ob.save()
    rules = competitorrules.objects.all()
    return render(request, 'thenx/rules_parser.html', {"rules": rules})

def rules_price_list(request):
    if request.method == "POST":
        dict = request.POST.dict()
        localcosttype = dict["localcosttype"]
        localcost = dict["cost"]
        type = dict["costtype"]
        ifsuppriceis = dict["HL"]
        than = dict["than"]
        thantype = dict["thantype"]
        supplier = dict["supplier"]
        ob = pricelistrules.objects.filter(supplier=supplier, localcosttype=localcosttype).first()
        if ob:
            ob.localcost = localcost
            ob.type = type
            ob.ifsuppriceis = ifsuppriceis
            ob.than = than
            ob.thantype = thantype
        else:
            ob = pricelistrules.objects.create(localcosttype=localcosttype, localcost=localcost, type=type, ifsuppriceis=ifsuppriceis,
                                               than=than, thantype=thantype, supplier=supplier)
        ob.save()
        pass
    suppliers = list(Product.objects.order_by('supplier').values_list("supplier", flat=True).distinct())
    rules = pricelistrules.objects.all()
    return render(request, 'thenx/rules_pricelist.html', {"suppliers": suppliers, "rules": rules})

def rules_margins(request):
    try:
        if request.method == "POST":
            dict = request.POST.dict()
            if dict["supcat"] == '' and dict["sku"] == '':
                messages.error(request, "Please select a supplier/category/sku.")
                raise Exception
            whichprice = dict["whichprice"]
            price = dict["cost"]
            pricetype = dict["pricetype"]
            appliedon = dict["appliedon"]
            if appliedon == 'sku':
                value = dict["sku"]
            else:
                value = dict["supcat"]

            ob = marginrules.objects.filter(whichprice=whichprice,appliedon=appliedon, value=value).first()
            if ob:
                ob.whichprice = whichprice
                ob.price = price
                ob.pricetype = pricetype
            else:
                ob = marginrules.objects.create(whichprice=whichprice, price=price, pricetype=pricetype, appliedon=appliedon, value=value)
            ob.save()
            pass
    except:
        pass
    rules = marginrules.objects.all()
    return render(request, 'thenx/rules_margin.html', {"rules": rules})

def rules_vat(request):
    if request.method == "POST":
        vat = request.POST.get("vat")
        if vatrules.objects.exists():
            ob = vatrules.objects.first()
            ob.vat = vat
        else:
            ob = vatrules.objects.create(vat=vat)
        ob.save()
    rules = vatrules.objects.all()
    return render(request, 'thenx/rules_vat.html', {"rules": rules})

def rules_warranty(request):
    if request.method == 'POST':
        dict = request.POST.dict()
        if dict["supcat"] == '' and dict["sku"] == '':
            messages.error(request, "Please select a supplier/category/sku.")
            raise Exception
        warranty = dict["warranty"]
        appliedon = dict["applyon"]
        if appliedon == 'sku':
            value = dict["sku"]
        else:
            value = dict["supcat"]
        ob = warrantyrules.objects.filter(appliedon=appliedon, value=value)
        if ob:
            ob.warranty = warranty
        else:
            ob = warrantyrules.objects.create(days=warranty, appliedon=appliedon, value=value)
        ob.save()

    rules = warrantyrules.objects.all()
    return render(request, 'thenx/rules_warranty.html', {"rules": rules})


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


def validateSKU(request):
    sku = request.GET.get('sku')
    p = Product.objects.filter(SKU__exact=sku).first()
    if p == None:
    #messages.error(request, "This product SKU does not exist")
        return HttpResponse(json.dumps({"result": "False"}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"result": "True"}), content_type='application/json')

def deleterule(request, ruleid, rule):
    if rule == "margin":
        marginrules.objects.get(pk=ruleid).delete()
        return redirect("thenx:marginsrules")
    elif rule == "parser":
        competitorrules.objects.get(pk=ruleid).delete()
        return redirect("thenx:parserrules")
    elif rule == "pricelist":
        pricelistrules.objects.get(pk=ruleid).delete()
        return redirect("thenx:pricelistrules")
    elif rule == "vat":
        vatrules.objects.get(pk=ruleid).delete()
        return redirect("thenx:vatrules")
    elif rule == "warranty":
        warrantyrules.objects.get(pk=ruleid).delete()
        return redirect("thenx:warrantyrules")
    else:
        print("Error")