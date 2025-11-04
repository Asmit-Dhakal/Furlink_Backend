
from django.db import models

class PetImage(models.Model):
	image = models.ImageField(upload_to='pet_gallery/')
	breed = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.breed} - {self.image.name}"
 