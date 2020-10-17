from django.contrib import admin
from .models import Product, Competitor_URL, Price_List
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('SKU', 'name',)
    search_fields = ('SKU','name')
    pass

@admin.register(Competitor_URL)
class Competitor_URLAdmin(admin.ModelAdmin):
    list_display = ('get_sku', 'get_name',)
    search_fields = ('product__SKU','product__name')
    def get_sku(self, obj):
        return obj.product.SKU
    get_sku.admin_order_field = 'product__SKU'  # Allows column order sorting
    get_sku.short_description = 'Product SKU'

    def get_name(self, obj):
        return obj.product.name
    get_name.admin_order_field = 'product__name'  # Allows column order sorting
    get_name.short_description = 'Product Name'
    pass


@admin.register(Price_List)
class Price_ListAdmin(admin.ModelAdmin):
    list_display = ('get_sku', 'get_name',)
    search_fields = ('product__SKU', 'product__name')
    pass

    def get_sku(self, obj):
        return obj.product.SKU
    get_sku.admin_order_field = 'product__SKU'  # Allows column order sorting
    get_sku.short_description = 'Product SKU'

    def get_name(self, obj):
        return obj.product.name
    get_name.admin_order_field = 'product__name'  # Allows column order sorting
    get_name.short_description = 'Product Name'