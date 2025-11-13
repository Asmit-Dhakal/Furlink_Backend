from django.db import models
from decimal import Decimal
from django.conf import settings
import uuid


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('name',)

	def __str__(self):
		return self.name


class Product(models.Model):
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
	name = models.CharField(max_length=200)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	image = models.ImageField(upload_to='product_images/', blank=True, null=True)
	is_available = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at', 'name')

	def __str__(self):
		return f"{self.name} ({self.category.name})"


class Order(models.Model):
	"""A simple Order model to store purchases containing multiple products.

	- user: the buyer
	- transaction: optional link to a payment.Transaction (set after payment)
	- total_amount: cached total paid/expected
	- status: pending -> paid -> fulfilled/cancelled
	"""
	STATUS_PENDING = 'pending'
	STATUS_PAID = 'paid'
	STATUS_CANCELLED = 'cancelled'
	STATUS_FULFILLED = 'fulfilled'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_PAID, 'Paid'),
		(STATUS_CANCELLED, 'Cancelled'),
		(STATUS_FULFILLED, 'Fulfilled'),
	]

	user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), on_delete=models.CASCADE, related_name='orders')
	transaction = models.ForeignKey('payment.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
	total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
	currency = models.CharField(max_length=10, default='USD')
	status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f"Order {self.pk} by {self.user} - {self.status} ({self.total_amount} {self.currency})"

	def recalc_total(self):
		"""Recalculate total_amount from related OrderItems and save."""
		total = Decimal('0.00')
		for item in self.items.all():
			total += (item.unit_price * item.quantity)
		self.total_amount = total.quantize(Decimal('0.01'))
		self.save(update_fields=['total_amount', 'updated_at'])


class OrderItem(models.Model):
	"""Line item for an Order. Stores snapshot of product price at time of purchase."""
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='+')
	quantity = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f"{self.quantity}× {self.product.name} @ {self.unit_price}"

	@property
	def line_total(self):
		return (self.unit_price * Decimal(self.quantity)).quantize(Decimal('0.01'))
	



class ShopPayment(models.Model):
	"""Shop-scoped payment record. Separate from global `payment.Transaction`.

	- order: the order this payment belongs to
	- user: optional user who initiated payment
	- tx_uuid: shop-local unique transaction id (UUID)
	- amount/currency/status: payment metadata
	- signature/raw_response: gateway metadata
	- credited: whether we've marked the order as paid/handled
	"""
	STATUS_PENDING = 'pending'
	STATUS_COMPLETED = 'completed'
	STATUS_FAILED = 'failed'

	STATUS_CHOICES = [
		(STATUS_PENDING, 'Pending'),
		(STATUS_COMPLETED, 'Completed'),
		(STATUS_FAILED, 'Failed'),
	]

	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shop_payments')
	user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), on_delete=models.SET_NULL, null=True, blank=True)
	tx_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	currency = models.CharField(max_length=10, default='USD')
	status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
	signature = models.CharField(max_length=512, null=True, blank=True)
	raw_response = models.JSONField(null=True, blank=True)
	credited = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f"ShopPayment {self.tx_uuid} for Order {getattr(self.order, 'id', None)} ({self.status})"



