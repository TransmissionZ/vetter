from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import *
from django.core.paginator import Paginator
from .models import *
from .tasks import *
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from datetime import timedelta
import json
import io
from django.core.files.storage import FileSystemStorage

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

    return render(request, 'thenx/login.html', {'form': form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')


@login_required(login_url='thenx:login')
def dash_view(request):
    totalp = Product.objects.count()
    totalc = Competitor_URL.objects.count()
    comp = Competitor_URL.objects.order_by('comp_name').values_list("comp_name", flat=True).distinct()

    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    tbrands = len(brands)
    suppliers = Product.objects.order_by("supplier").values_list("supplier", flat=True).distinct()
    categories = Product.objects.order_by("category").values_list("category", flat=True).distinct()
    categories = ", ".join(categories)
    categories = categories.split(', ')
    categories = list(set(categories))
    tcats = len(categories)
    delta = datetime.now() - timedelta(days=1)
    recentlychanged = Product.objects.filter(dateupdated__gte=delta)
    increased = 0
    decreased = 0
    for o in recentlychanged:
        if o.price_list_set.first().finalprice > o.oldprice:
            increased += 1
        else:
            decreased += 1

    recentlychanged = recentlychanged.count()
    imcheapest = 0
    imcheaper = 0
    imaverage = 0
    imhigher = 0
    imhighest = 0
    imequal = 0
    for p in Product.objects.all():
        comp_prices = list(p.competitor_url_set.order_by('comp_price').values_list('comp_price', flat=True))
        if len(comp_prices) == 0:
            imequal += 1
            continue
        price = round(p.price_list_set.first().finalprice, 1)
        comp_prices.append(price)
        comp_prices.sort()
        idx = comp_prices.index(price)
        if len(set(comp_prices)) <= 1:
            imequal += 1
            continue

        if idx == 0:
            imcheapest += 1
        elif 0 < idx < len(comp_prices)//2:
            imcheaper += 1
        elif idx == len(comp_prices)//2:
            imaverage += 1
        elif len(comp_prices)//2 < idx < len(comp_prices) - 1:
            imhigher += 1
        else:
            imhighest += 1

    pindex = 96.91
    complist = [[] for _ in range(len(comp))]

    for idx, c in enumerate(complist):
        comp_name = list(comp)[idx]
        complist[idx].append(comp_name)
        complist[idx].append(Competitor_URL.objects.filter(comp_name__contains=comp_name).count())
        complist[idx].append(40)
        complist[idx].append(0)

    complist.insert(0, ["thenx", Product.objects.count(), 96.5, 0])

    comp = comp.count()
    if request.method == 'GET':
        brandq = False
        supq = False
        catq = False
        if 'q' in request.GET:
            query = request.GET.get('q')
            plist = Product.objects.filter(
                Q(SKU__icontains=query) | Q(name__icontains=query) | Q(brand__icontains=query))
        else:
            plist = Product.objects.all()

        if 'brand' in request.GET:
            brandq = True
            query = request.GET.get('brand')
            if query != 'All' and query != None:
                plist = Product.objects.filter(Q(brand__icontains=query))
            else:
                plist = Product.objects.all()

        if 'supplier' in request.GET:
            supq = True
            query = request.GET.get('supplier')
            if query != 'All' and query != None:
                plist = Product.objects.filter(Q(supplier__icontains=query))
            else:
                plist = Product.objects.all()

        if 'category' in request.GET:
            catq = True
            query = request.GET.get('category')
            print(query)
            if query != 'All' and query != None:
                plist = Product.objects.filter(category__icontains=query)
            else:
                plist = Product.objects.all()

    paginator = Paginator(plist, 100)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    # UpdateDB()
    return render(request, 'thenx/dashboard.html', {
        'totalp': totalp,
        'totalc': totalc,
        'comp': comp,
        'list': products,
        'brands': brands,
        'recentlychanged': recentlychanged,
        'suppliers': suppliers,
        'categories': categories,
        'tcats': tcats,
        'tbrands': tbrands,
        'increased': increased,
        'decreased': decreased,
        'imcheapest': imcheapest,
        'imcheaper': imcheaper,
        'imaverage': imaverage,
        'imhigher': imhigher,
        'imhighest': imhighest,
        'imequal': imequal,
        'pindex': pindex,
        'complist': complist,
        })


def get_count_users():
    return User.objects.count()

def competitors_upload(request):
    if request.method == "POST":
        compurls = request.FILES["compurls"]
        p = UploadCompetitors.objects.create(upload_file=compurls)
        # print(p)
        upload_comps()
        print(compurls)

        return JsonResponse({"result": "True"})
    else:
        return JsonResponse({"result": "False"})
@login_required(login_url='thenx:login')
def products_view(request):
    # UpdateDB()
    brands = Product.objects.order_by("brand").values_list("brand", flat=True).distinct()
    plist = Product.objects.all()
    suppliers = Product.objects.order_by("supplier").values_list("supplier", flat=True).distinct()
    categories = Product.objects.order_by("category").values_list("category", flat=True).distinct()
    # categories = list(set(x for l in categories for x in l))
    categories = ", ".join(categories)
    categories = categories.split(', ')
    categories = list(set(categories))

    if request.method == "POST":
        urldata = request.POST.dict()
        url = urldata.get("url")
        p = urldata.get("product")
        p = Product.objects.filter(SKU=p).first()
        if p.competitor_url_set.filter(url=url).count() == 0:
            c = p.competitor_url_set.create(url=url)
            c.scrap()
            p.update_competitorprices()
        else:
            messages.error(request, "This URL Already Exists")
        queryflag1 = False
        queryflag2 = False
        if 'q' in request.GET:
            query = request.GET.get('q')
            queryflag1 = True
            return HttpResponseRedirect('.' + '?q=' + str(query))

        if 'brand' in request.GET:
            bquery = request.GET.get('brand')
            queryflag2 = True
            return HttpResponseRedirect('.' + '?brand=' + str(bquery))

        # if queryflag1 or queryflag2:
        #     return HttpResponseRedirect('.' + '?brand=' + str(bquery) + '&' + 'q=' + str(query))
        # elif queryflag1:
        #     return HttpResponseRedirect('.' + '?q=' + str(query))
        # elif queryflag2:
        #     return HttpResponseRedirect('./' + '?brand=' + str(bquery))
        # else:
        return redirect('thenx:products')

    if request.method == "GET":
        if 'q' in request.GET:
            query = request.GET.get('q')
            print(query)
            plist = Product.objects.filter(
                Q(SKU__icontains=query) | Q(name__icontains=query) | Q(brand__icontains=query))
        else:
            plist = Product.objects.all()

        if 'brand' in request.GET:
            brandq = True
            query = request.GET.get('brand')
            if query != 'All' and query != None:
                plist = Product.objects.filter(Q(brand__icontains=query))
            else:
                plist = Product.objects.all()

        if 'supplier' in request.GET:
            supq = True
            query = request.GET.get('supplier')
            if query != 'All' and query != None:
                plist = Product.objects.filter(Q(supplier__icontains=query))
            else:
                plist = Product.objects.all()

        if 'category' in request.GET:
            catq = True
            query = request.GET.get('category')
            if query != 'All' and query != None:
                plist = Product.objects.filter(category__icontains=query)
            else:
                plist = Product.objects.all()

    paginator = Paginator(plist, 50)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'thenx/products.html', {
        'list': products,
        'brands': brands,
        'suppliers': suppliers,
        'categories': categories,
        'uploadform': upload_comps,
    })


@login_required(login_url='thenx:login')
def deleteurl(request, urlid=None, pid=None):
    o = Competitor_URL.objects.filter(pk=urlid).first()
    p = o.product
    o.delete()
    p.update_competitorprices()

    for o in competitorrules.objects.filter(Q(appliedon="sup", value__icontains=p.supplier) |
                                            Q(appliedon='cat', value__icontains=p.category) |
                                            Q(appliedon='sku', value=p.SKU)):
        set_default_competitorprice(o.pk)

    dict = request.POST.dict()
    if 'q' in request.POST:
        return HttpResponseRedirect(reverse('thenx:products') + "?q=" + dict['q'])
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
    return HttpResponseRedirect(reverse('thenx:products')+"?q="+sku)
    # return HttpResponseRedirect('.' + '?brand=All' + '&' + 'q=' + sku)


@login_required(login_url='thenx:login')
def rules_view(request):
    totalcomps = [_ for _ in range(
        Competitor_URL.objects.order_by('comp_name').values_list("comp_name", flat=True).distinct().count())]
    # UpdateDB()
    # testcelery.delay()
    return render(request, 'thenx/rules.html', {'totalcomps': totalcomps})


def rules_parser(request):
    if request.method == "POST":
        dict = request.POST.dict()
        if "supcat" in dict:
            if dict["supcat"] == '' and dict["sku"] == '':
                messages.error(request, "Please select a supplier/category/sku.")
                return redirect("thenx:parserrules")
        else:
            if "sku" in dict:
                if dict["sku"] == '':
                    messages.error(request, "Please select a valid sku.")
                    return redirect("thenx:parserrules")
        priceshouldbe = dict["HL1"]
        than = dict["than1"]
        butnotlowerthan = dict["notlowerthan"]
        try:
            than = float(than)
            butnotlowerthan = float(butnotlowerthan)
        except:
            messages.error(request, "All costs should be in numbers.")
            return redirect("thenx:parserrules")
        thantype = dict["thantype"]
        if thantype.lower() == "ron":
            thantype = competitorrules.RON
        else:
            thantype = competitorrules.P
        thanHL = dict["HL2"]
        competitor = dict["comp"]
        appliedon = dict["applyon"]
        if appliedon == 'sku':
            value = dict["sku"]
        else:
            value = dict["supcat"]
        butnotlowerthantype = dict["notlowerthantype"]
        if butnotlowerthantype.lower() == "ron":
            butnotlowerthantype = competitorrules.RON
        else:
            butnotlowerthantype = competitorrules.P
        ob = competitorrules.objects.filter(appliedon=appliedon, value=value).first()
        if ob:
            ob.than = than
            ob.thantype = thantype
            ob.butnotlowerthantype = butnotlowerthantype
            ob.butnotlowerthan = butnotlowerthan
            ob.priceshouldbe = priceshouldbe
            ob.thanHL = thanHL
            ob.competitor = competitor
        else:
            ob = competitorrules.objects.create(priceshouldbe=priceshouldbe, than=than, thantype=thantype,
                                                thanHL=thanHL,
                                                competitor=competitor, butnotlowerthan=butnotlowerthan,
                                                butnotlowerthantype=butnotlowerthantype, appliedon=appliedon, value=value)
        ob.save()
        update_competitor(priceshouldbe, than, thantype, thanHL, competitor, butnotlowerthan, butnotlowerthantype, appliedon, value)
    rules = competitorrules.objects.all()
    total_comps = Competitor_URL.objects.order_by('comp_name').values_list("comp_name", flat=True).distinct()
    return render(request, 'thenx/rules_parser.html', {"rules": rules, "totalcomps":total_comps})


def rules_price_list(request):
    if request.method == "POST":
        dict = request.POST.dict()
        if "supcat" in dict:
            if dict["supcat"] == '' and dict["sku"] == '':
                messages.error(request, "Please select a supplier/category/sku.")
                return redirect("thenx:pricelistrules")
        else:
            if "sku" in dict:
                if dict["sku"] == '':
                    messages.error(request, "Please select a valid sku.")
                return redirect("thenx:pricelistrules")

        localcosttype = dict["localcosttype"]
        localcost = dict["cost"]
        try:
            localcost = float(localcost)
        except:
            messages.error(request, "Enter cost in float")
            return redirect("thenx:pricelistrules")
        type = dict["costtype"]
        if type.lower() == "ron":
            type = pricelistrules.RON
        else:
            type = pricelistrules.P
        ifsuppriceis = dict["HL"]
        than = dict["than"]
        # thantype = dict["thantype"]
        thantype = pricelistrules.RON
        appliedon = dict["applyon"]
        if appliedon == 'sku':
            value = dict["sku"]
        else:
            value = dict["supcat"]
        ob = pricelistrules.objects.filter(appliedon=appliedon, value=value, localcosttype=localcosttype).first()
        if ob:
            ob.localcost = localcost
            ob.type = type
            ob.ifsuppriceis = ifsuppriceis
            ob.than = than
            ob.thantype = thantype
            ob.save()
        else:
            ob = pricelistrules.objects.create(localcosttype=localcosttype, localcost=localcost, type=type,
                                               ifsuppriceis=ifsuppriceis,
                                               than=than, thantype=thantype, appliedon=appliedon, value=value,)
            # ob.save()
        update_pricelist(localcosttype, localcost, type, ifsuppriceis, than, thantype, appliedon, value)

    rules = pricelistrules.objects.all()
    return render(request, 'thenx/rules_pricelist.html', {"rules": rules})


def rules_margins(request):
    try:
        if request.method == "POST":
            dict = request.POST.dict()
            if "supcat" in dict:
                if dict["supcat"] == '' and dict["sku"] == '':
                    messages.error(request, "Please select a supplier/category/sku.")
                    raise Exception
            else:
                if dict["sku"] == '':
                    messages.error(request, "Please select a valid sku.")
                    raise Exception
            whichprice = dict["whichprice"]
            price = dict["cost"]
            try:
                price = float(price)
            except:
                messages.error(request, "Please enter a valid amount.")
                raise Exception
            pricetype = dict["pricetype"]
            if pricetype.lower() == "ron":
                pricetype = marginrules.RON
            else:
                pricetype = marginrules.P
            appliedon = dict["appliedon"]
            if appliedon == 'sku':
                value = dict["sku"]
            else:
                value = dict["supcat"]

            ob = marginrules.objects.filter(whichprice=whichprice, appliedon=appliedon, value=value).first()
            if ob:
                ob.whichprice = whichprice
                ob.price = price
                ob.pricetype = pricetype
                ob.save()
            else:
                ob = marginrules.objects.create(whichprice=whichprice, price=price, pricetype=pricetype,
                                                appliedon=appliedon, value=value)

            update_margins(whichprice, price, pricetype, appliedon, value)
    except Exception as e:
        print(e)
    rules = marginrules.objects.all()
    return render(request, 'thenx/rules_margin.html', {"rules": rules})


def rules_vat(request):
    if request.method == "POST":
        vat = request.POST.get("vat")
        try:
            vat = float(vat)
        except:
            messages.error(request, "Please enter a valid number for VAT.")
            return redirect("thenx:vatrules")
        if vatrules.objects.exists():
            ob = vatrules.objects.first()
            ob.vat = vat
        else:
            ob = vatrules.objects.create(vat=vat)
        ob.save()
        updatevat(vat=vat)
    rules = vatrules.objects.all()
    return render(request, 'thenx/rules_vat.html', {"rules": rules})


def rules_warranty(request):
    if request.method == 'POST':
        dict = request.POST.dict()
        if "supcat" in dict:
            if dict["supcat"] == '' and dict["sku"] == '':
                messages.error(request, "Please select a supplier/category/sku.")
                return redirect("thenx:warrantyrules")
        else:
            if dict["sku"] == '':
                messages.error(request, "Please select a valid sku.")
                return redirect("thenx:warrantyrules")

        warranty = dict["warranty"]
        try:
            warranty = int(warranty)
        except:
            messages.error(request, "Please enter number of days properly.")
            return redirect("thenx:warrantyrules")
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
        update_warranty(warranty, appliedon, value)

    rules = warrantyrules.objects.all()
    return render(request, 'thenx/rules_warranty.html', {"rules": rules})


def getDetails(request):
    choice = request.GET.get('choice', '')
    if choice == 'cat':
        all_cats = Product.objects.order_by('category').values_list("category", flat=True).distinct()
        all_cats = ", ".join(all_cats)
        result_set = all_cats.split(', ')
        result_set = list(set(result_set))
        #result_set = list(set(x for l in all_cats for x in l))
    elif choice == 'sup':
        result_set = list(Product.objects.order_by('supplier').values_list("supplier", flat=True).distinct())
    else:
        result_set = []
    return HttpResponse(json.dumps(result_set), content_type='application/json')

def downloadpricelist(request):
    plist = Price_List.objects.all()
    pricelistcsv = "SKU,Categories,Description,Supplier Name,Supplier Price,Local Cost Supplier," \
                   "Local Cost ThenX,VAT,All Product Cost,Margin Wholesale,Wholesale Price,Margin Shop Price," \
                   "Retail Price,Gross Profit WholeSale,Margin Wholesale,Gross Profit Shop,Margin Shop\n"
    for p in plist:
        try:
            grossprofitshop = p.retailprice - p.allproductcost
        except:
            grossprofitshop = 0.0
        cats = p.product.category
        cats = cats.split(',')
        cats = [c.strip() for c in cats]
        cats = ' | '.join(cats)
        desc = p.product.name
        desc = desc.replace(',', '-')
        supplier = p.product.supplier.replace(', ', ' - ')
        pricelistcsv += f"{p.product.SKU},{cats},{desc},{supplier}," \
                        f"{p.product.base_cost},{p.localcostsupplier}," \
                        f"{p.localcostthenx},{p.vat},{p.allproductcost},{p.wsprice}," \
                        f"{p.wspricefinal}," \
                        f"{p.retailprice},{p.retailpricefinal},{p.gpws},{p.margin_ws},{grossprofitshop},{p.margin_shop}\n"
    obj = io.StringIO()
    obj.write(pricelistcsv)
    obj.seek(0)
    response = HttpResponse(obj.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ThenX PriceList ' + str(datetime.now().date()) + '.csv"'
    return response

def validateSKU(request):
    sku = request.GET.get('sku')
    p = Product.objects.filter(SKU__exact=sku).first()
    if p == None:
        # messages.error(request, "This product SKU does not exist")
        return HttpResponse(json.dumps({"result": "False"}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"result": "True"}), content_type='application/json')


def deleterule(request, ruleid, rule):
    if rule == "margin":
        set_default_margin(ruleid)
        return redirect("thenx:marginsrules")
    elif rule == "parser":
        set_default_competitorprice(ruleid)
        return redirect("thenx:parserrules")
    elif rule == "pricelist":
        set_default_pricelist(ruleid)
        return redirect("thenx:pricelistrules")
    elif rule == "vat":
        vatrules.objects.get(pk=ruleid).delete()
        set_default_vat()
        return redirect("thenx:vatrules")
    elif rule == "warranty":
        set_default_warranty(ruleid)
        return redirect("thenx:warrantyrules")
    else:
        print("Error")
        return None
