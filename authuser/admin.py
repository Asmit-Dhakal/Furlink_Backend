
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from .models import Account
from django.utils.html import format_html


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # include commonly edited fields on user creation
        fields = ('username', 'email', 'first_name', 'middle_name', 'last_name')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = (
        'username', 'email', 'first_name', 'middle_name', 'last_name', 'is_active',
        'kyc_status', 'kyc_verified_date', 'profile_photo_thumb', 'kyc_doc_front_thumb', 'kyc_doc_back_thumb'
    )
    list_filter = ('is_active', 'kyc_status', 'gender', 'province', 'district')
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
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def profile_photo_thumb(self, obj):
        if obj and getattr(obj, 'profile_photo', None):
            try:
                url = obj.profile_photo.url
            except Exception:
                return '-'
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', url)
        return '-'
    profile_photo_thumb.short_description = 'Profile Photo'

    def kyc_doc_front_thumb(self, obj):
        if obj and getattr(obj, 'kyc_doc_front', None):
            try:
                url = obj.kyc_doc_front.url
            except Exception:
                return '-'
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', url)
        return '-'
    kyc_doc_front_thumb.short_description = 'KYC Front'

    def kyc_doc_back_thumb(self, obj):
        if obj and getattr(obj, 'kyc_doc_back', None):
            try:
                url = obj.kyc_doc_back.url
            except Exception:
                return '-'
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:4px;" />', url)
        return '-'
    kyc_doc_back_thumb.short_description = 'KYC Back'


# register Account for quick admin access
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'currency', 'updated_at')
    search_fields = ('user__username', 'user__email')

