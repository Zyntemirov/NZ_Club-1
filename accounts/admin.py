from django.contrib import admin
from .models import User, userProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _


# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = userProfile
    can_delete = False

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['agent', 'gender', 'region', 'view_count', 'balance', 'withdrawn_balance', 'image', 'birth_date']
        return ['agent', 'gender', 'region', 'image', 'birth_date']


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'groups'),
        }),
    )
    list_display = ('username', 'email', 'date_joined', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('email',)
    inlines = (UserProfileInline,)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['phone', 'email', 'first_name', 'last_name', 'is_staff']
        return ['phone', 'email', 'first_name', 'last_name']


admin.site.register(User, UserAdmin)
admin.site.site_header = "Nz Club"
