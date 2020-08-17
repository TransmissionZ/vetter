from django.db import models
import re
from datetime import datetime
from django.utils import timezone
from .scrappers import *
# Create your models here.

class Product(models.Model):
    SKU = models.CharField(max_length=32)
    name = models.TextField()
    price = models.FloatField(default=0.0)
    brand = models.TextField()
    originalurl = models.TextField()
    dateupdated = models.DateTimeField()
    important = models.BooleanField(default=False)

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
    lastupdated = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.comp_name

    def scrap(self):
        if 'gsmnet.ro' in self.url:
            ob = gsmnet(self.url)
        elif 'sepmobile.ro' in self.url:
            ob = sepmobile(self.url)

        price = ob.scrap()
        self.comp_price = price
        print(self.comp_price)
        self.save()



    def save(self, *args, **kwargs):
        self.lastupdated = timezone.now()
        try:
            n = re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))', self.url)
            self.comp_name = n[0]
        except Exception as e:
            n = self.url.find('/')
            if n < 8:
                n1 = self.url.find('.')
                self.comp_name = self.url[n+1:n1]
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