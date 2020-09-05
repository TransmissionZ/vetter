from django.db import models
import re
from datetime import datetime
from django.utils import timezone
from .scrappers import *
from django_mysql.models import JSONField
import math
# from .tasks import updatevat
from huey.contrib.djhuey import periodic_task, task
# Create your models here.

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


class Product(models.Model):
    SKU = models.CharField(max_length=32)
    name = models.TextField()
    price = models.FloatField(default=0.0)
    base_cost = models.FloatField(default=0.0)
    brand = models.TextField()
    originalurl = models.TextField()
    dateupdated = models.DateTimeField()
    important = models.BooleanField(default=False)
    # category = JSONField(default=list)
    category = models.TextField(default='')
    supplier = models.TextField(default='')
    highestcompprice = models.FloatField(default=0.0)
    lowestcompprice = models.FloatField(default=0.0)
    avgcompprice = models.FloatField(default=0.0)

    def update_price(self, price):
        self.price = price
        self.dateupdated = timezone.now()

    def update_competitorprices(self):
        prices = list(self.competitor_url_set.all().values_list("comp_price", flat=True))
        prices = list(filter((0.0).__ne__, prices))
        self.highestcompprice = max(p for p in prices)
        self.lowestcompprice = min(p for p in prices)
        self.avgcompprice = sum(prices) / len(prices)
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

        def __unicode__(self):
            return self.name


class Price_List(models.Model):
    RON = "RON"
    P = "%"
    TYPE_CHOICE = (
        (RON, "Ron"),
        (P, "%")
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    finalprice = models.FloatField(default=0.0)
    competitorprice = models.FloatField(default=0.0)
    localcostsupplier = models.FloatField(default=0.0)
    localcostsuppliertype = models.CharField(max_length=3, choices=TYPE_CHOICE, default=RON)
    localcostthenx = models.FloatField(default=0.0)
    localcostthenxtype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    wsprice = models.FloatField(default=0.0)  # Whole Sale
    wspricetype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    retailprice = models.FloatField(default=0.0)
    retailpricetype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    warranty = models.IntegerField(default=0)
    vat = models.FloatField(default=0.0)
    allproductcost = models.FloatField(default=0.0)
    gpws = models.FloatField(default=0.0)  # Gross Profit Wholesale
    margin_ws = models.FloatField(default=0.0)
    gp_shop = models.FloatField(default=0.0)
    margin_shop = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.finalprice)

    def save(self, *args, **kwargs):
        self.finalprice = self.product.base_cost
        try:
            self.finalprice = float(self.finalprice)
        except:
            self.finalprice = 0.0
        self.product.dateupdated = timezone.now()
        if self.localcostsuppliertype == self.RON and self.localcostsupplier != 0.0:
            self.finalprice += self.localcostsupplier
        else:
            if self.localcostsupplier != 0.0:
                self.finalprice *= 1 + self.localcostsupplier / 100
        if self.localcostthenxtype == self.RON and self.localcostthenx != 0.0:
            self.finalprice += self.localcostthenx
        else:
            if self.localcostthenx != 0.0:
                self.finalprice *= 1 + self.localcostthenx / 100
        if self.vat != 0.0:
            self.finalprice *= 1 + (self.vat / 100)
        self.allproductcost = self.finalprice
        if self.wspricetype == self.RON and self.wsprice != 0.0:
            self.finalprice += self.wsprice
        else:
            if self.wsprice != 0.0:
                self.finalprice *= 1 + self.wsprice / 100
        self.finalprice = normal_round(self.finalprice)
        if self.retailpricetype == self.RON and self.retailprice != 0.0:
            self.finalprice += self.retailprice
        else:
            if self.retailprice != 0.0:
                self.finalprice *= 1 + self.retailprice / 100

        self.finalprice = normal_round(self.finalprice)
        self.finalprice = self.finalprice - 0.01
        self.gpws = self.allproductcost - self.wsprice
        self.margin_ws = normal_round(((self.finalprice - self.allproductcost) / self.finalprice) * 100)
        return super(Price_List, self).save(*args, **kwargs)


class Competitor_URL(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    url = models.TextField()
    comp_name = models.TextField()
    comp_price = models.FloatField(default=0.0)
    lastupdated = models.DateTimeField()

    def __str__(self):
        return self.comp_name

    def scrap(self):
        ob = None
        if 'gsmnet.ro' in self.url:
            ob = gsmnet(self.url)
        elif 'sepmobile.ro' in self.url:
            ob = sepmobile(self.url)
        elif 'sunex.ro' in self.url:
            ob = sunex(self.url)
        elif 'conectshop.ro' in self.url:
            ob = conectshop(self.url)
        elif 'magazingsm.ro' in self.url:
            ob = magazingsm(self.url)
        elif 'protableta.ro' in self.url:
            ob = protableta(self.url)
        elif 'powerlaptop.ro' in self.url:
            ob = powerlaptop(self.url)
        elif 'servicepack.ro' in self.url:
            ob = servicepack(self.url)
        elif 'distrizone.ro' in self.url:
            ob = distrizone(self.url)
        elif 'moka-gsm.ro' in self.url:
            ob = mokagsm(self.url)
        elif 'inowgsm.ro' in self.url:
            ob = inowgsm(self.url)
        else:
            print("BRAND NOT AVAILABLE FOR " + str(self.url))
        price = ob.scrap()
        self.comp_price = price
        print(self.comp_price)
        self.save()

    def save(self, *args, **kwargs):
        self.lastupdated = timezone.now()
        self.product.update_competitorprices()
        try:
            if 'www' in self.url:
                if 'powerlaptop.ro' in self.url:
                    self.comp_name = 'powerlaptop'
                elif 'distrizone.ro' in self.url:
                    self.comp_name = 'distrizone'
                elif 'moka-gsm.ro' in self.url:
                    self.comp_name = 'moka-gsm'
                else:
                    n = re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))', self.url)
                    self.comp_name = n[0]
            else:
                raise Exception
        except Exception as e:
            n = self.url.find('/')
            if n < 8:
                n1 = self.url.find('.')
                self.comp_name = self.url[n + 2:n1]
            else:
                n1 = self.url.find('.')
                self.comp_name = self.url[:n1]
        return super(Competitor_URL, self).save(*args, **kwargs)


class vatrules(models.Model):
    vat = models.FloatField(default=0)


class warrantyrules(models.Model):
    CAT = "CAT"
    SUP = "SUP"
    SKU = "SKU"
    CHOICES = (
        (CAT, "cat"),
        (SUP, "sup"),
        (SKU, "sku")
    )

    days = models.IntegerField(default=0)
    appliedon = models.CharField(max_length=3, choices=CHOICES, default=SKU)
    value = models.TextField(default='')


class marginrules(models.Model):
    CAT = "CAT"
    SUP = "SUP"
    SKU = "SKU"
    CHOICES = (
        (CAT, "cat"),
        (SUP, "sup"),
        (SKU, "sku")
    )
    RON = "RON"
    P = "%"
    TYPE_CHOICE = (
        (RON, "Ron"),
        (P, "%")
    )
    WS = "WHOLESALE"
    RETAIL = "RETAIL"
    whichpricechoices = (
        (WS, "Wholesale"),
        (RETAIL, "Retail")
    )
    whichprice = models.CharField(max_length=10, choices=whichpricechoices, default=WS)
    price = models.FloatField(default=0.0)
    pricetype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    appliedon = models.CharField(max_length=3, choices=CHOICES, default=SKU)
    value = models.TextField(default='')


class pricelistrules(models.Model):
    HIGH = "HIGH"
    LOW = "LOW"
    EQUALTO = "EQUALTO"
    HLCHOICES = (
        (HIGH, "High"),
        (LOW, "Low"),
        (EQUALTO, "Equals")
    )
    RON = "RON"
    P = "%"
    TYPE_CHOICE = (
        (RON, "Ron"),
        (P, "%")
    )
    SUP = "SUP"
    THENX = "THENX"
    OPTIONS = (
        (SUP, "Supplier"),
        (THENX, "Thenx")
    )
    CAT = "CAT"
    SUP = "SUP"
    SKU = "SKU"
    CHOICES = (
        (CAT, "cat"),
        (SUP, "sup"),
        (SKU, "sku")
    )

    appliedon = models.CharField(max_length=3, choices=CHOICES, default=SKU)
    value = models.TextField(default='')
    localcosttype = models.CharField(max_length=15, choices=OPTIONS, default=SUP)
    localcost = models.FloatField(default=0.0)
    type = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    ifsuppriceis = models.CharField(max_length=7, choices=HLCHOICES, default=HIGH)
    than = models.FloatField(default=0.0)
    thantype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    supplier = models.TextField(default='')


class competitorrules(models.Model):
    HIGH = "HIGH"
    LOW = "LOW"
    EQUALTO = "EQUALTO"
    HLCHOICES = (
        (HIGH, "High"),
        (LOW, "Low"),
        (EQUALTO, "Equals")
    )
    RON = "RON"
    P = "%"
    TYPE_CHOICE = (
        (RON, "Ron"),
        (P, "%")
    )
    SUP = "SUP"
    THENX = "THENX"
    OPTIONS = (
        (SUP, "Supplier"),
        (THENX, "Thenx")
    )
    CAT = "CAT"
    SUP = "SUP"
    SKU = "SKU"
    CHOICES = (
        (CAT, "cat"),
        (SUP, "sup"),
        (SKU, "sku")
    )
    priceshouldbe = models.CharField(max_length=7, choices=HLCHOICES, default=HIGH)
    than = models.FloatField(default=0.0)
    thantype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    thanHL = models.CharField(max_length=10, choices=HLCHOICES, default=HIGH)
    competitor = models.TextField(default='')
    butnotlowerthan = models.FloatField(default=0.0)
    butnotlowerthantype = models.CharField(max_length=4, choices=TYPE_CHOICE, default=RON)
    appliedon = models.CharField(max_length=3, choices=CHOICES, default=SKU)
    value = models.TextField(default='')
