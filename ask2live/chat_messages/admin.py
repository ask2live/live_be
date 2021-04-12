from django.contrib import admin

from . import models
# Register your models here.

@admin.register(models.Message)
class ChatMessagesAdmin(admin.ModelAdmin):
    # sent_timestamp.admin_order_field = 'timefield'
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
    # time_seconds.short_description = 'Precise Time'    

    # list_display = ('id', 'time_seconds', )
