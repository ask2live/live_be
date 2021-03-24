from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.
@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ("Custom Profile", { "fields" : (
            "nickname","profile_image","hole_open_auth","work_field","login_method","followed_count","following_count","social_account","bio","rating","work_company",
            
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    list_display= ("pk","email","nickname","work_field","hole_open_auth","login_method","social_account","rating","work_company")
    ordering = ("-pk",'email',)
