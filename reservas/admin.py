from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "service", "date", "time", "created_at")
    list_filter = ("service", "date")
    search_fields = ("name", "email", "phone")
