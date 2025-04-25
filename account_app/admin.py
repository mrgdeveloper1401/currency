from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ContentDevice, PrivateNotification, PublicNotification, UserLoginLog


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'email', 'verify_level', 'is_staff', 'is_active')
    list_filter = ('verify_level', 'is_staff', 'is_active')
    search_fields = ('username', 'phone', 'email')
    ordering = ('-created_at',)
    list_per_page = 20

    fieldsets = (
        (None, {'fields': ('username', 'phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', "user_image")}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Verification', {'fields': ('verify_level',)}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(ContentDevice)
class ContentDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_model', 'device_os', 'ip_address', 'is_blocked')
    list_filter = ('is_blocked', 'device_os')
    search_fields = ('user__username', 'device_number', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(PrivateNotification)
class PrivateNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'body', 'user__username')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(PublicNotification)
class PublicNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'body')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at')
    search_fields = ('user__username', 'ip_address')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    list_per_page = 20
