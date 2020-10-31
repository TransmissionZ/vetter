from __future__ import absolute_import, unicode_literals
import requests
import json
from django.utils import timezone
from .models import Product, pricelistrules, marginrules, warrantyrules, competitorrules, UploadCompetitors
from django.db.models import Count, Q
from bs4 import BeautifulSoup as soup
from huey import crontab
import huey
from huey.contrib.djhuey import periodic_task, task, db_task, db_periodic_task
import random
import pytz
import http.client
import csv

@db_task()
def upload_comps():
    p = UploadCompetitors.objects.latest('pk')
    with open(p.upload_file.path, 'rt', encoding="utf8") as f_input:
        csv_input = csv.reader(f_input)
        for idx, r in enumerate(csv_input):
            if idx == 0:
                continue
            r = [i for i in r if i]
            for i, link in enumerate(r):
                if i == 0:
                    sku = link
                else:
                    p = Product.objects.filter(SKU=sku).first()
                    if p.competitor_url_set.filter(url=link).count() == 0:
                        c = p.competitor_url_set.create(url=link)
                        c.scrap()
                        p.update_competitorprices()
                        print("R!")
                        for o in competitorrules.objects.filter(Q(appliedon="sup", value__icontains=p.supplier) |
                                            Q(appliedon='cat', value__icontains=p.category) |
                                            Q(appliedon='sku', value=p.SKU)):
                            print("R")
                            set_default_competitorprice(o.pk)

@db_periodic_task(crontab(minute='*/30'))
def UpdateDB():
    print("Updating Database")
    conn = http.client.HTTPSConnection("thenx.net")

    headers = {
        'cache-control': "no-cache",
    }

    conn.request("GET", "/rest/V1/thenx/prfeed/", headers=headers)

    res = conn.getresponse()
    data = res.read()

    r = data.decode('utf-8')
    conn.close()
    a = json.loads(json.loads(r))
    
    # Product.objects.all().delete()
    # Code for deleting Duplicates
    rem_dup = Product.objects.values('SKU').annotate(SKU_count=Count('SKU')).filter(SKU_count__gt=1)
    for data in rem_dup:
        sku = data["SKU"]
        p = Product.objects.filter(SKU=sku).order_by('pk')
        for i, p1 in enumerate(p):
            if i != 0:
                p1.delete()
    count = 0
    for product in a:
        count += 1
        if count % 500 == 0:
            print("Products done: " + str(count))
        p = Product.objects.filter(SKU=product["sku"]).first()
        if p:
            if p.price != product['price']:
                price = product['price']
                if price == None or str(price) == 'nan':
                    price = 0.0
                p.update_price(price)
            if p.originalurl != product['url']:
                p.originalurl = product['url']
            if p.name != product['name']:
                p.name = product['name']
            if p.brand != product['brand']:
                p.brand = product['brand']
            cat = json.loads(product['cat'])
            cat = ", ".join(cat)

            if p.category != cat:
                p.category = cat
            if p.supplier != product['supplier']:
                p.supplier = product['supplier']

            cost = product['cost']
            if cost == None or str(cost) == 'nan':
                cost = 0.0
            if p.base_cost != cost:
                p.base_cost = cost
            p.save()
        else:
            price = product['price']
            if price == None or str(price) == 'nan':
                price = 0.0
            cost = product['cost']
            if cost == None or str(cost) == 'nan':
                cost = 0.0

            cat = json.loads(product['cat'])
            cat = ", ".join(cat)
            p = Product.objects.create(SKU=product['sku'], name=product['name'], price=price,
                                       brand=product['brand'],
                                       originalurl=product['url'],
                                       category=cat, supplier=product['supplier'],
                                       base_cost=cost, dateupdated=timezone.now())
            # p.save()
            p.price_list_set.create(finalprice=cost)

@task()
def updatevat(vat):
    print("VAT Update Started...")
    ps = Product.objects.all()
    for p in ps:
        o = p.price_list_set.first()
        o.vat = vat
        o.save()
    print("VAT Updated.")

@task()
def update_warranty(warranty, appliedon, value):
    if appliedon == "sku":
        p = Product.objects.filter(SKU=value).first()
        p = p.price_list_set.first()
        p.warranty = warranty
        p.save()
    else:
        if appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

        for p in plist:
            o = p.price_list_set.first()
            o.warranty = warranty
            o.save()

@task()
def update_margins(whichprice, price, pricetype, appliedon, value):
    if appliedon == "sku":
        p = Product.objects.filter(SKU=value).first()
        o = p.price_list_set.first()
        if whichprice == "wholesale":
            o.wsprice = price
            o.wspricetype = pricetype
        else:
            o.retailprice = price
            o.retailpricetype = pricetype
        o.save()
    else:
        if appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

        for p in plist:
            o = p.price_list_set.first()
            if whichprice == "wholesale":
                o.wsprice = price
                o.wspricetype = pricetype
            else:
                o.retailprice = price
                o.retailpricetype = pricetype
            o.save()

@task()
def update_pricelist(localcosttype, localcost, type, ifsuppriceis,than, thantype, appliedon, value):
    if appliedon == "sku":
        plist = Product.objects.filter(SKU=value)
    else:
        if value == "all":
            plist = Product.objects.all()
        elif appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

    for p in plist:
        supprice = p.base_cost
        o = p.price_list_set.first()
        if (ifsuppriceis == "Higher" and supprice > float(than)) or \
                (ifsuppriceis == "Lower" and supprice < float(than)) or (ifsuppriceis == "Equal to" and supprice == float(than)):
            if localcosttype == "Supplier":
                o.localcostsupplier = localcost
                o.localcostsuppliertype = type
            else:
                o.localcostthenx = localcost
                o.localcostthenxtype = type
            o.save()

@task()
def update_competitor(priceshouldbe, than, thantype, thanHL, competitor, butnotlowerthan, butnotlowerthantype, appliedon, value):
    if appliedon == "sku":
        plist = Product.objects.filter(SKU=value)
    else:
        if appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

    for p in plist:
        finalprice = p.price_list_set.first().finalprice
        if competitor == "all":
            competitors = list(p.competitor_url_set.all().values_list("comp_price"))
        else:
            competitor = int(competitor)
            if competitor > p.competitor_url_set.all().count():
                competitor = p.competitor_url_set.all().count()

            totalcomps = p.competitor_url_set.all().values_list('id')
            rand = list(random.sample(list(totalcomps), min(len(totalcomps), competitor)))
            rand = [i for sub in rand for i in sub]
            competitors = p.competitor_url_set.filter(id__in=rand)
            competitors = list(competitors.values_list('comp_price'))

        competitors = [i for sub in competitors for i in sub]
        if competitors:
            if thanHL == "highest":
                competitorprice = p.highestcompprice # max(sub for sub in competitors)
            elif thanHL == "cheapest":
                competitorprice = p.lowestcompprice # min(sub for sub in competitors)
            else:
                competitorprice = p.avgcompprice # sum(competitors)/len(competitors)
        else:
            continue


        if butnotlowerthantype == "RON":
            calcprice = finalprice + butnotlowerthan
        else:
            calcprice = finalprice * (1 + (butnotlowerthan / 100))

        if thantype == "RON":
            if priceshouldbe == "higher":
                newprice = competitorprice + than
            elif priceshouldbe == "cheaper":
                newprice = competitorprice - than
        else:
            if priceshouldbe == "higher":
                newprice = competitorprice * (1 + (than/100))
            elif priceshouldbe == "cheaper":
                newprice = competitorprice * (1 - (than / 100))

        if newprice < calcprice:
            fprice = calcprice
        else:
            fprice = newprice

        o = p.price_list_set.first()
        o.competitorprice = fprice
        o.save()


@db_task()
def set_default_competitorprice(ruleid):
    o = competitorrules.objects.get(pk=ruleid)
    appliedon = o.appliedon
    value = o.value
    if appliedon == "sku":
        plist = Product.objects.filter(SKU=value)
    else:
        if appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

    for p in plist:
        finalprice = p.price_list_set.first().finalprice
        if o.competitor == "all":
            competitors = list(p.competitor_url_set.all().values_list("comp_price"))
        else:
            o.competitor = int(o.competitor)
            if o.competitor > p.competitor_url_set.all().count():
                o.competitor = p.competitor_url_set.all().count()

            totalcomps = p.competitor_url_set.all().values_list('id')
            rand = list(random.sample(list(totalcomps), min(len(totalcomps), o.competitor)))
            rand = [i for sub in rand for i in sub]
            competitors = p.competitor_url_set.filter(id__in=rand)
            competitors = list(competitors.values_list('comp_price'))

        competitors = [i for sub in competitors for i in sub]
        if competitors:
            if o.thanHL == "highest":
                competitorprice = p.highestcompprice  # max(sub for sub in competitors)
            elif o.thanHL == "cheapest":
                competitorprice = p.lowestcompprice  # min(sub for sub in competitors)
            else:
                competitorprice = p.avgcompprice  # sum(competitors)/len(competitors)
        else:
            continue

        if o.butnotlowerthantype == "RON":
            calcprice = finalprice + o.butnotlowerthan
        else:
            calcprice = finalprice * (1 + (o.butnotlowerthan / 100))

        if o.thantype == "RON":
            if o.priceshouldbe == "higher":
                newprice = competitorprice + o.than
            elif o.priceshouldbe == "cheaper":
                newprice = competitorprice - o.than
        else:
            if o.priceshouldbe == "higher":
                newprice = competitorprice * (1 + (o.than / 100))
            elif o.priceshouldbe == "cheaper":
                newprice = competitorprice * (1 - (o.than / 100))

        if newprice < calcprice:
            fprice = calcprice
        else:
            fprice = newprice
        print("FPRICE: " + str(fprice))
        p2 = p.price_list_set.first()
        p2.competitorprice = fprice
        p2.save()
        # o = p.price_list_set.first()
        # if o.competitorprice != 0.0:
        #     o.competitorprice = 0.0
        #     o.save()

def set_default_pricelist(ruleid):
    o = pricelistrules.objects.get(pk=ruleid)
    appliedon = o.appliedon
    value = o.value
    if appliedon == "sku":
        plist = Product.objects.filter(SKU=value)
    else:
        if appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier__icontains=value)

    for p in plist:
        if o.localcosttype == "Supplier":
            if p.price_list_set.first().localcostsupplier != 0.0:
                p.price_list_set.first().localcostsupplier = 0.0
                p.save()
        else:
            if p.price_list_set.first().localcostthenx != 0.0:
                p.price_list_set.first().localcostthenx = 0.0
                p.save()
    o.delete()

@db_task()
def set_default_vat():
    plist = Product.objects.all()
    for p in plist:
        o = p.price_list_set.first()
        if o.vat != 0.0:
            o.vat = 0.0
            o.save()

@db_task()
def set_default_margin(ruleid):
    o = marginrules.objects.get(pk=ruleid)
    if o.appliedon == 'sku':
        value = o.value
        ob = Product.objects.filter(SKU=value).first()
        if o.whichprice == "wholesale":
            ob.wsprice = 0.0
        else:
            ob.retailprice = 0.0
        ob.save()
    else:
        value = o.value
        if o.appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier=value)
        for p in plist:
            ob = p.price_list_set.first()
            if o.whichprice == "wholesale":
                ob.wsprice = 0.0
            else:
                ob.retailprice = 0.0
            ob.save()
    o.delete()

@db_task()
def set_default_warranty(ruleid):
    o = warrantyrules.objects.get(pk=ruleid)
    if o.appliedon == 'sku':
        value = o.value
        ob = Product.objects.filter(SKU=value).first()
        ob = ob.price_list_set.first()
        ob.warranty = 0
        ob.save()
    else:
        value = o.value
        if o.appliedon == "cat":
            plist = Product.objects.filter(category__icontains=value)
        else:
            plist = Product.objects.filter(supplier=value)
        for p in plist:
            ob = p.price_list_set.first()
            ob.warranty = 0
            ob.save()
    o.delete()

@task()
def ExportChangedPrices():
    pass