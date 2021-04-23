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
        ,"sent_timestamps"
    )
    def sent_timestamps(self, obj):
        return obj.sent_timestamp.strftime("%d %b %Y %H:%M:%S")