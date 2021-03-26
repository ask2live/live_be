from django.contrib import admin

from . import models
# Register your models here.

@admin.register(models.Message)
class ChatMessagesAdmin(admin.ModelAdmin):
    list_display = (
        "id"
        ,"__str__"
        ,"text"
        ,"sender"
        ,"livehole"
        ,"sent_timestamp"
    )