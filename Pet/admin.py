from django.contrib import admin
from .models import Pet

admin.site.register(Pet)  # Add your models inside the list to register them