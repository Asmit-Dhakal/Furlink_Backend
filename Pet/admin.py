from django.contrib import admin
from django.utils.html import format_html
from .models import Pet, Adoption


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'name', 'species', 'breed', 'owner', 'age', 'gender', 'color', 'weight', 'adoption_status'
	)
	search_fields = ('name', 'breed', 'owner__username')
	list_filter = ('species', 'breed', 'gender')
	raw_id_fields = ('owner',)
	readonly_fields = ()
	fieldsets = (
		(None, {
			'fields': ('owner', 'name', 'species', 'breed', 'age', 'gender')
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
		adoption = getattr(obj, 'adoptions', None)
		if adoption:
			status = 'Adopted' if adoption.is_adopted else 'Pending'
			return format_html('<span>{}</span>', status)
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
