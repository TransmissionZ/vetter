from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery.task import periodic_task
import requests
import json
from django.utils import timezone
from .models import Product
from django.db.models import Count
from bs4 import BeautifulSoup as soup


# @periodic_task(
#     run_every=(crontab(minute='*/60')),
#     name="updatedb",
#     ignore_result=True
# )
def UpdateDB():
    print("Updating Database")
    # p = Product(SKU=123, name="TEST NAME", price=1000.1, originalurl='www.thenx.com',
    #             dateupdated=timezone.now())
    # p.save()
    url = 'http://dev.thenx.net/rest/V1/thenx/prfeed/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 7h5om9dna1pljz1mkbwqr4pzxcih1m79',
    }
    r = requests.get(url, headers=headers)
    a = json.loads(r.json())
    # Product.objects.all().delete()
    # Code for deleting Duplicates
    rem_dup = Product.objects.values('SKU').annotate(SKU_count=Count('SKU')).filter(SKU_count__gt=1)

    for data in rem_dup:
        sku = data["SKU"]
        p = Product.objects.filter(SKU=sku).order_by('pk')
        for i, p1 in enumerate(p):
            if i != 0:
                p1.delete()

    for product in a:
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
            if p.category != json.loads(product['cat']):
                p.category = json.loads(product['cat'])
            if p.supplier != product['supplier']:
                p.supplier = product['supplier']
            if p.base_cost != product['cost']:
                p.base_cost = product['cost']
            p.save()
        else:
            price = product['price']
            if price == None or str(price) == 'nan':
                price = 0.0
            cost = product['cost']
            if cost == None or str(cost) == 'nan':
                cost = 0.0
            p = Product(SKU=product['sku'], name=product['name'], price=price, brand=product['brand'], originalurl=product['url'],
                        category=json.loads(product['cat']), supplier=product['supplier'], base_cost=cost)
            p.save()

