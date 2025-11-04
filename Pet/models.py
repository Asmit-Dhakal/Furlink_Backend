from django.db import models
from authuser.models import User

# Create your models here.

class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_pets')
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
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.species}) - Owner: {self.owner.username}"


class Adoption(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.CASCADE, related_name='adoptions')
    adopter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adopted_pets')
    adoption_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    is_adopted = models.BooleanField(default=False)

    def __str__(self):
        status = 'Adopted' if self.is_adopted else 'Pending'
        return f"Adoption of {self.pet.name} by {self.adopter.username} - Status: {status}"