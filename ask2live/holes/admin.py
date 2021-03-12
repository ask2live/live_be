from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Hole)
class HoleAdmin(admin.ModelAdmin):
    list_display = (
        "title"
        ,"subtitle"
        ,"description"
        ,"create_date"
        ,"reserved_date"
        ,"finished_date"
        ,"wish_user_list"
        ,"status"
        ,"target_demand"
        ,"host_id"
    )

@admin.register(models.LiveHole)
class LiveHoleAdmin(admin.ModelAdmin):
    list_display = (
    "hole"
    ,"livehole_user_ids"
    ,
    )