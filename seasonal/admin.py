from django.contrib import admin
from seasonal.models import *
from adminsortable2.admin import SortableAdminMixin


class ViewStoriesAdmin(admin.ModelAdmin):
    list_display = ['user', 'stories', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'stories']


@admin.register(Stories)
class StoriesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'image', 'video']
    list_display_links = list_display

    exclude = ('views',)


@admin.register(SeasonalVideo)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'category', 'status', 'is_active', 'get_owner_region']
    list_select_related = ('owner', 'category')
    list_display_links = ['owner', 'title', 'category']
    search_fields = ['title', 'text']
    list_filter = ['owner__username']
    exclude = ('favorites', 'views', 'is_active', 'watched_videos')
    list_per_page = 50
    autocomplete_fields = ['owner']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def make_activation(self, request, queryset):
        queryset.update(status='2')

    def get_owner_region(self, obj):
        return f'{obj.owner.profile.get_region_display()}'

    make_activation.short_description = 'Активировать'
    get_owner_region.short_description = 'Регион'

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['title', 'text', 'video', 'category', 'type', 'is_top', 'image', 'owner', 'status']
        else:
            return ['title', 'text', 'video', 'category', 'type', 'image', 'owner', ]

    def get_inline_instances(self, request, obj=None):
        if request.user.is_superuser:
            return [inline(self.model, self.admin_site) for inline in
                    self.inlines]
        return []

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            # do push notif soon
            super().save_model(request, obj, form, change)
        else:
            obj.status = '3'
            obj.is_active = False
            super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class SeasonalCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'create_at']
    search_fields = ['text']


class RequestAdmin(admin.ModelAdmin):
    list_display = ['category', 'phone', 'create_at', 'is_checked']
    search_fields = ['phone', ]


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'bonus', 'video', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'video']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(video__owner=request.user)


admin.site.register(ViewStories, ViewStoriesAdmin)
admin.site.register(ComplaintStories)
admin.site.register(SeasonalComment, SeasonalCommentAdmin)
admin.site.register(Request, RequestAdmin)
