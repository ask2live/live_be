from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Hole)
class HoleAdmin(admin.ModelAdmin):
    list_display = (
        "id"
        ,"title"
        ,"reserve_date"
        ,"finish_date"
        ,"status"
        ,"rating"
        ,"host"
    )

@admin.register(models.LiveHole)
class LiveHoleAdmin(admin.ModelAdmin):
    list_display = (
    "hole"
    # ,"participants"
    ,"__str__"
    ,"host_uid"
    ,"audience_list"
    ,"room_number"
    )