from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
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