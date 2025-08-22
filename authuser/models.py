from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPERUSER = "SUPERUSER", "Superuser"
        PET_OWNER = "PET_OWNER", "Pet Owner"
        PET_ADOPTER = "PET_ADOPTER", "Pet Adopter"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PET_OWNER
    )

    middle_name = models.CharField(max_length=50, blank=True, null=True)
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

    def is_pet_owner(self):
        return self.role == self.Roles.PET_OWNER

    def is_pet_adopter(self):
        return self.role == self.Roles.PET_ADOPTER

    def is_superuser_role(self):
        return self.role == self.Roles.SUPERUSER