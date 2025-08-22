from django.db import models
from authuser.models import User

# Create your models here.

class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_pets')
    keeper = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='kept_pets', null=True, blank=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # e.g., Dog, Cat
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(help_text="Age in years", blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(help_text="Weight in kg", blank=True, null=True)
    health_issues = models.TextField(blank=True, null=True)
    vaccination_status = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('CheckedOut', 'Checked Out'), ('Inactive', 'Inactive')], default='Active')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.species}) - Owner: {self.owner.username}"
