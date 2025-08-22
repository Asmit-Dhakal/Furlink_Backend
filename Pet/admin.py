from django.contrib import admin
from .models import Pet
from django.utils.html import format_html
from django import forms

class PetAdminForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = '__all__'
        widgets = {
            'status': forms.Select(attrs={'class': 'pet-status-select'}),
            'gender': forms.Select(attrs={'class': 'pet-gender-select'}),
        }
    class Media:
        css = {
            'all': ('admin/css/custom_pet_admin.css',)
        }

class PetAdmin(admin.ModelAdmin):
    form = PetAdminForm
    list_display = (
        'name', 'species', 'breed', 'owner', 'keeper', 'status', 'admission_date', 'pet_photo_thumb'
    )
    search_fields = ('name', 'species', 'breed', 'owner__username', 'keeper__username')
    list_filter = ('species', 'status', 'admission_date', 'owner', 'keeper')
    raw_id_fields = ('owner', 'keeper')
    readonly_fields = ('admission_date', 'pet_photo_thumb')
    fieldsets = (
        (None, {
            'fields': ('name', 'species', 'breed', 'age', 'gender', 'color', 'weight', 'description')
        }),
        ('Ownership', {
            'fields': ('owner', 'keeper')
        }),
        ('Health & Status', {
            'fields': ('health_issues', 'vaccination_status', 'status')
        }),
        ('Photo & Dates', {
            'fields': ('photo', 'pet_photo_thumb', 'admission_date')
        }),
    )

    def pet_photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:4px;" />', obj.photo.url)
        return "-"
    pet_photo_thumb.short_description = 'Photo'

admin.site.register(Pet, PetAdmin)
