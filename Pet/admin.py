from django.contrib import admin
from django.utils.html import format_html
from .models import Pet, Adoption, Category, AdoptionPrice


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	search_fields = ('name',)


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'name', 'species', 'breed', 'category', 'owner', 'age', 'gender', 'color', 'weight', 'adoption_status'
	)
	search_fields = ('name', 'breed', 'owner__username')
	list_filter = ('species', 'breed', 'gender', 'category')
	raw_id_fields = ('owner',)
	readonly_fields = ()
	fieldsets = (
		(None, {
			'fields': ('owner', 'name', 'species', 'breed', 'category', 'age', 'gender')
		}),
		('Appearance & Health', {
			'fields': ('color', 'weight', 'health_issues', 'vaccination_status', 'photo')
		}),
		('Description', {
			'fields': ('description',)
		}),
	)

	def adoption_status(self, obj):
		# show adoption status if an Adoption exists
		from .models import Adoption as AdoptionModel
		try:
			adoption = AdoptionModel.objects.get(pet=obj)
			status = 'Adopted' if adoption.is_adopted else 'Pending'
			return format_html('<span>{}</span>', status)
		except AdoptionModel.DoesNotExist:
			return format_html('<span>{}</span>', 'Not Adopted')
	adoption_status.short_description = 'Adoption Status'



@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
	list_display = ('id', 'pet', 'adopter', 'adoption_date', 'is_adopted')
	search_fields = ('pet__name', 'adopter__username')
	list_filter = ('is_adopted', 'adoption_date')
	raw_id_fields = ('pet', 'adopter')
	readonly_fields = ('adoption_date',)
	fieldsets = (
		(None, {
			'fields': ('pet', 'adopter')
		}),
		('Adoption Details', {
			'fields': ('adoption_date', 'is_adopted', 'remarks')
		}),
	)


@admin.register(AdoptionPrice)
class AdoptionPriceAdmin(admin.ModelAdmin):
	list_display = ('id', 'category', 'adopter', 'price', 'currency', 'is_active', 'effective_from', 'effective_to')
	search_fields = ('category__name', 'adopter__username')
	list_filter = ('is_active', 'currency')
	raw_id_fields = ('adopter',)
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		(None, {
			'fields': ('category', 'adopter', 'price', 'currency', 'is_active')
		}),
		('Validity', {
			'fields': ('effective_from', 'effective_to')
		}),
	)
