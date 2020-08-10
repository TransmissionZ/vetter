from __future__ import absolute_import, unicode_literals
# from celery.schedules import crontab
# from celery.task import periodic_task
import requests
import json
from django.utils import timezone
from .models import Product
from django.db.models import Count

# @periodic_task(
#     run_every=(crontab(minute='*/60')),
#     name="updatedb",
#     ignore_result=True
# )
def UpdateDB():
    # print("Updating Database")
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
            p.save()
        else:
            price = product['price']
            if price == None or str(price) == 'nan':
                price = 0.0

            #print(timezone.now().strftime('%Y-%m-%d %H:%M'))
            p = Product(SKU=product['sku'], name=product['name'], price=price, brand=product['brand'], originalurl=product['url'])
            p.save()
