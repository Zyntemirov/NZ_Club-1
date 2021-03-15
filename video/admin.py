from django.contrib import admin

# Register your models here.
from video.models import *


class TariffInline(admin.TabularInline):
    model = Tariff

    def has_add_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'category', 'status']
    list_display_links = ['owner', 'title', 'category']
    search_fields = ['title', 'text']
    list_filter = ['owner__username']
    inlines = [TariffInline]
    exclude = ('favorites', 'views', 'is_active', 'watched_videos')
    list_per_page = 50
    autocomplete_fields = ['owner', ]
    list_select_related = ['owner']
    list_editable = ['status', ]

    # Test

    # radio_fields = {'status':admin.VERTICAL}
    # fields = ('title',)
    # actions = ['make_activation']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def make_activation(self, request, queryset):
        queryset.update(status='2')

    make_activation.short_description = 'Активировать'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['title']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'create_at']
    search_fields = ['text']


class FAQAdmin(admin.ModelAdmin):
    list_display = ['question']
    search_fields = ['question', 'reply']


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


class ViewBannerAdmin(admin.ModelAdmin):
    list_display = ['user', 'banner', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'banner']


class VideoTrainingAdmin(admin.ModelAdmin):
    list_display = ['title', 'video']
    list_display_links = list_display


class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'video', 'block']
    list_display_links = list_display
    list_filter = ['block']

    exclude = ('views',)

    # def has_add_permission(self, request):
    #     if len(Banner.objects.all()) > 12:
    #         return False
    #     return True


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(ViewBanner, ViewBannerAdmin)
admin.site.register(VideoTraining, VideoTrainingAdmin)
