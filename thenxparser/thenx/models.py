from django.db import models
import re
from datetime import datetime
from django.utils import timezone
from .scrappers import *
from django_mysql.models import JSONField
# Create your models here.

class Product(models.Model):
    SKU = models.CharField(max_length=32)
    name = models.TextField()
    price = models.FloatField(default=0.0)
    base_cost = models.FloatField(default=0.0)
    brand = models.TextField()
    originalurl = models.TextField()
    dateupdated = models.DateTimeField()
    important = models.BooleanField(default=False)
    category = JSONField(default=list)
    supplier = models.TextField(default='')

    def update_price(self, price):
        self.price = price
        self.dateupdated = datetime.now().strftime("%d/%m/%Y %H:%M")


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.dateupdated = timezone.now()
        return super(Product, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']

        def __unicode__(self):
            return self.name


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
                self.comp_name = self.url[n+2:n1]
            else:
                n1 = self.url.find('.')
                self.comp_name = self.url[:n1]
        return super(Competitor_URL, self).save(*args, **kwargs)
    # def (self):
    #     print('called')
    #     try:
    #         n = re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))', self.url)
    #         self.comp_name = n[0]
    #         self.save()
    #     except Exception as e:
    #         self.comp_name = self.url
    #         self.save()