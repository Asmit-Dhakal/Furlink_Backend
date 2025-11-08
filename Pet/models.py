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
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')
    ], blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    health_issues = models.TextField(blank=True, null=True)
    vaccination_status = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_available_for_adoption = models.BooleanField(default=True)

    # ✅ Custom adoption price (optional)
    custom_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return f"{self.name} ({self.species})"

    @property
    def adoption_price(self):
        """
        Priority: pet.custom_price → category.active AdoptionPrice → 0.00
        """
        if self.custom_price is not None:
            return self.custom_price

        today = timezone.localdate()
        price = (AdoptionPrice.objects
                 .filter(category=self.category, is_active=True)
                 .filter(models.Q(effective_from__lte=today) | models.Q(effective_from__isnull=True))
                 .filter(models.Q(effective_to__gte=today) | models.Q(effective_to__isnull=True))
                 .first())
        return price.price if price else Decimal('0.00')

class Adoption(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='adoption')
    adopter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoptions')
    adoption_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        status = 'Confirmed' if self.is_confirmed else 'Pending'
        return f"{self.pet.name} → {self.adopter.username} ({status})"

class AdoptionPrice(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='adoption_prices')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(blank=True, null=True)
    effective_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.name}: {self.price} {self.currency}"

    def is_current(self):
        today = timezone.localdate()
        if self.effective_from and today < self.effective_from:
            return False
        if self.effective_to and today > self.effective_to:
            return False
        return self.is_active