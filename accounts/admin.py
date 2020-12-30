from django.contrib import admin
from .models import User, userProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _


# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = userProfile
    can_delete = False


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
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'date_joined', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('email',)
    inlines = (UserProfileInline,)


admin.site.register(User, UserAdmin)
admin.site.site_header = "Nz Club"
