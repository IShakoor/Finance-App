from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models.user import CustomUser

# Admin class, defines admin role
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Plaid', {'fields': ('plaid_access_token',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    list_display = ('email', 'username', 'is_staff', 'is_active', 'date_joined')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)