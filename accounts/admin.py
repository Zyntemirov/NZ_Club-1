from django.contrib import admin
from .models import User, userProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import Notification


class UserProfileInline(admin.StackedInline):
    model = userProfile
    can_delete = False

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['agent', 'gender', 'region', 'view_count', 'balance', 'withdrawn_balance', 'image', 'birth_date']
        return ['agent', 'gender', 'region', 'image', 'birth_date']


class UserAdmin(BaseUserAdmin):
    list_display = ['phone', 'username', 'is_active']
    inlines = (UserProfileInline,)
    fieldsets = (
        (None, {'fields': ('phone', 'username', 'password')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )
    fieldsets_subadmin = (
        (None, {'fields': ('phone', 'username', 'password')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'password1', 'password2'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )
    add_fieldsets_subadmin = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'password1', 'password2'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            if not obj:
                return self.add_fieldsets
            return self.fieldsets
        else:
            if not obj:
                return self.add_fieldsets_subadmin
            return self.fieldsets_subadmin

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user_profile = userProfile.objects.get(user=request.user)
        if request.user.is_superuser:
            return qs
        return qs.filter(profile__region=user_profile.region)


admin.site.register(User, UserAdmin)
admin.site.register(Notification)
admin.site.site_header = "Nz Club"
