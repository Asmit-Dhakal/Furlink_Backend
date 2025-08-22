from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django.utils.html import format_html
from django import forms

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'kyc_status': forms.Select(attrs={'class': 'kyc-status-select'}),
            'role': forms.Select(attrs={'class': 'role-select'}),
        }
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminForm
    list_display = (
        'username', 'email', 'first_name', 'middle_name', 'last_name', 'role', 'is_active',
        'kyc_status', 'kyc_verified_date', 'profile_photo_thumb', 'kyc_doc_front_thumb', 'kyc_doc_back_thumb'
    )
    list_filter = ('role', 'is_active', 'kyc_status', 'gender', 'province', 'district')
    search_fields = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'citizenship_number', 'contact_number')
    readonly_fields = (
        'last_login', 'date_joined', 'kyc_verified_date', 'profile_photo_thumb', 'kyc_doc_front_thumb', 'kyc_doc_back_thumb'
    )
    raw_id_fields = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'middle_name', 'last_name', 'email', 'date_of_birth', 'gender',
                'contact_number', 'profile_photo', 'profile_photo_thumb'
            )
        }),
        ('Address', {
            'fields': (
                'province', 'district', 'municipality', 'ward', 'tole', 'house_number'
            )
        }),
        ('Citizenship', {
            'fields': (
                'citizenship_number', 'citizenship_issue_district', 'citizenship_issue_date'
            )
        }),
        ('KYC', {
            'fields': (
                'kyc_doc_front', 'kyc_doc_front_thumb', 'kyc_doc_back', 'kyc_doc_back_thumb',
                'kyc_status', 'kyc_verified_date', 'kyc_remarks'
            )
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def profile_photo_thumb(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.profile_photo.url)
        return "-"
    profile_photo_thumb.short_description = 'Profile Photo'

    def kyc_doc_front_thumb(self, obj):
        if obj.kyc_doc_front:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.kyc_doc_front.url)
        return "-"
    kyc_doc_front_thumb.short_description = 'KYC Front'

    def kyc_doc_back_thumb(self, obj):
        if obj.kyc_doc_back:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', obj.kyc_doc_back.url)
        return "-"
    kyc_doc_back_thumb.short_description = 'KYC Back'
