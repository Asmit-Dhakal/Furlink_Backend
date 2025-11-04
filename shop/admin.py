from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_at', 'updated_at')
	search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'price', 'discount_price', 'is_available', 'created_at')
	list_filter = ('category', 'is_available')
	search_fields = ('name', 'description')
	readonly_fields = ('created_at', 'updated_at')
	raw_id_fields = ('category',)

	def image_thumb(self, obj):
		if obj.image:
			return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
		return '-'
	image_thumb.short_description = 'Image'
