from django.contrib import admin
from .models import *
# Register your models here.


# admin.site.register(Restaurant)
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    change_form_template = 'bulk_import/change.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['restaurant_id'] = object_id
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )


admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(RestaurantHours)
admin.site.register(SpecialDays)
admin.site.register(Order)
admin.site.register(TableNumber)
admin.site.register(OrderItem)
admin.site.register(Favorite)