from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Reservation)
class HoleReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id"
        ,"hole"
        ,"status"
        ,"reserve_date"
        ,"finish_date"
        ,"target_demand"
        ,"current_demand"
        ,"guests_list"
    )

