from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.Request)
class RequestAdmin(admin.ModelAdmin):
    list_display= (
        "questions"
        ,"user"
        ,"hole"
        ,"create_date"
    )