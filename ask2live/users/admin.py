from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.
@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ("Custom Profile", { "fields" : (
            "profile_image",
            "work_field",
            "work_company",
            "bio",
            "uid",
            
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    list_display= (
        "pk",
        "uid",
        "username",
        "work_field",
        "work_company")
    ordering = ("-pk",'username',)

@admin.register(models.UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = (
    "id",
    "user_id"
    ,"following_user_id"
    ,"created"
    )