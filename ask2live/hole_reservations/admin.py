from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Reservation)
class HoleReservationAdmin(admin.ModelAdmin):
    list_display = (
    "hole"
    ,"status"
    ,"reserve_start_date"
    ,"finish_date"
    ,"target_demand"
    ,"__str__"
    )