from django.contrib import admin
from .models import Pet, Adoption, Category, AdoptionPrice
# Register your models here.
admin.site.register(Pet)
admin.site.register(Adoption)
admin.site.register(Category)
admin.site.register(AdoptionPrice)
