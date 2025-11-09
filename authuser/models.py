from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    province = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=10, blank=True, null=True)
    tole = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=20, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    citizenship_number = models.CharField(max_length=30, blank=True, null=True)
    citizenship_issue_district = models.CharField(max_length=50, blank=True, null=True)
    citizenship_issue_date = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    kyc_doc_front = models.ImageField(upload_to='kyc_docs/front/', blank=True, null=True)
    kyc_doc_back = models.ImageField(upload_to='kyc_docs/back/', blank=True, null=True)
    KYC_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
    ]
    kyc_status = models.CharField(max_length=10, choices=KYC_STATUS_CHOICES, default="PENDING")
    kyc_verified_date = models.DateTimeField(blank=True, null=True)
    kyc_remarks = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='authuser_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='authuser_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )



class Account(models.Model):
    """Account for a user to store balance for adoptions/payments."""
    user = models.OneToOneField('authuser.User', on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return f"Account({self.user.username}): {self.balance} {self.currency}"

    def can_charge(self, amount: Decimal) -> bool:
        return self.balance >= amount

    def charge(self, amount: Decimal):
        if amount < Decimal('0'):
            raise ValueError('amount must be non-negative')
        if not self.can_charge(amount):
            raise ValueError('insufficient funds')
        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])

    def topup(self, amount: Decimal):
        if amount < Decimal('0'):
            raise ValueError('amount must be non-negative')
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])


# create Account automatically when a User is created
@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.get_or_create(user=instance)
