from django.contrib import admin

# Register your models here.
from video.models import *


class TariffInline(admin.TabularInline):
    model = Tariff


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['owner', 'title', 'category']
    list_display_links = list_display
    search_fields = ['title', 'text']
    list_filter = ['owner__username']
    inlines = [TariffInline]
    exclude = ('favorites', 'views', 'is_active', 'watched_videos')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    search_fields = ['title']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'create_at']
    search_fields = ['text']


class ReplyAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'create_at', 'comment']
    search_fields = ['text']


class FAQAdmin(admin.ModelAdmin):
    list_display = ['question']
    search_fields = ['question', 'reply']


class RequestAdmin(admin.ModelAdmin):
    list_display = ['category', 'phone', 'create_at', 'is_checked']
    search_fields = ['phone', ]


class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'bonus', 'video', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'video']


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
admin.site.register(Reply, ReplyAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(ViewHistory, ViewHistoryAdmin)
admin.site.register(ViewBanner, ViewBannerAdmin)
admin.site.register(VideoTraining, VideoTrainingAdmin)
