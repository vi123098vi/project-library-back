from django.contrib import admin #
from django.contrib.auth.admin import UserAdmin #注册我的用户模型
from .models import *

admin.site.register(Book)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'phone')}),
        ('权限', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
admin.site.register(User,CustomUserAdmin)

