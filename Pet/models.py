from django.db import models
from django.utils import timezone
from decimal import Decimal

from authuser.models import User



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pet Category'
        verbose_name_plural = 'Pet Categories'

    def __str__(self):
        return self.name


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # e.g., Dog, Cat
    breed = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    age = models.PositiveIntegerField(help_text="Age in years", blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(help_text="Weight in kg", blank=True, null=True)
    health_issues = models.TextField(blank=True, null=True)
    vaccination_status = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        owner = getattr(self.owner, 'username', None)
        return f"{self.name} ({self.species}) - Owner: {owner}"


class Adoption(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='adoptions')
    adopter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adopted_pets')
    adoption_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    is_adopted = models.BooleanField(default=False)

    def __str__(self):
        status = 'Adopted' if self.is_adopted else 'Pending'
        return f"Adoption of {self.pet.name} by {self.adopter.username} - Status: {status}"


class AdoptionPrice(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='adoption_prices')
    adopter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='adoption_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(blank=True, null=True)
    effective_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Adoption Price'
        verbose_name_plural = 'Adoption Prices'

    def __str__(self):
        adopter_part = f' for {self.adopter.username}' if self.adopter else ''
        return f"{self.category.name}: {self.price} {self.currency}{adopter_part}"

    def is_current(self):
        today = timezone.localdate()
        if self.effective_from and today < self.effective_from:
            return False
        if self.effective_to and today > self.effective_to:
            return False
        return self.is_active
