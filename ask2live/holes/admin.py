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
    "id"
    ,"hole"
    # ,"participants"
    ,"__str__"
    ,"host_uid"
    ,"audience_uids"
    )

@admin.register(models.Participants)
class ParticipantsAdmin(admin.ModelAdmin):
    list_display = (
    "id"
    ,"livehole"
    ,"user"
    ,"joined"
    ,"leaved"
    )

@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
    "id"
    ,"user"
    ,"hole"
    ,"question"
    ,"is_voice"
    ,"is_answered"
    )