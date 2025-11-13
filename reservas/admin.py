from django.contrib import admin
from .models import Reservation
from .models import Offering


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "service", "date", "time", "created_at")
    list_filter = ("service", "date")
    search_fields = ("name", "email", "phone")
@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'price_eur', 'slug')
    prepopulated_fields = {'slug': ('name',)}
