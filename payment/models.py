from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid


# Basic Transaction model to record eSewa payment attempts and status.
class Transaction(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_COMPLETED = 'completed'
	STATUS_FAILED = 'failed'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_COMPLETED, 'Completed'),
		(STATUS_FAILED, 'Failed'),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
	)
	# Use a UUIDField with a module-level callable default so migrations can serialize it.
	tx_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=8, default='NPR')
	status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
	signature = models.CharField(max_length=512, blank=True, null=True)
	raw_response = models.JSONField(null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Transaction {self.tx_uuid} ({self.status})"
