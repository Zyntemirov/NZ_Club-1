from django.contrib import admin
from seasonal.models import *
from adminsortable2.admin import SortableAdminMixin
from django.utils.safestring import mark_safe


class RoomInline(admin.TabularInline):
    model = Room

    def has_add_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True


class ImageInline(admin.TabularInline):
    model = ApartmentImage
    fields = ('image', 'apartment')
    readonly_fields = ('download_img', )

    def has_add_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True
    
    def download_img(self, obj):
        return mark_safe(f'<a href="{obj.image.url}" download >скачать</a>')

    download_img.short_description = 'Скачать изображение'


class ViewStoriesAdmin(admin.ModelAdmin):
    list_display = ['user', 'stories', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'stories']


@admin.register(Stories)
class StoriesAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'image', 'video']
    list_display_links = list_display

    exclude = ('views',)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'entry_date', 'exit_date', 'room', 'phone']
    list_display_links = list_display


@admin.register(SeasonalApartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ['is_checked', 'name', 'address', 'phone', 'category', 'city', 'type', 'create_at']
    list_display_links = list_display
    exclude = ('favorites', 'views', 'likes', 'watched_videos',)
    inlines = [RoomInline, ImageInline]
    readonly_fields = ('download_video', 'download_img')
    fields = ('name', 'description', 'address', 'phone', ('video_by_user', 'download_video'),
            'video_link', 'category', 'city', ('cover_image', 'download_img'), 'is_checked', 'type', 'owner')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.order_by('is_checked')
        return qs.filter(owner=request.user)

    def get_owner_region(self, obj):
        return f'{obj.owner.profile.get_region_display()}'

    get_owner_region.short_description = 'Регион'

    def get_inline_instances(self, request, obj=None):
        if request.user.is_superuser:
            return [inline(self.model, self.admin_site) for inline in self.inlines]
        return []
    
    def download_video(self, obj):
        return mark_safe(f'<a href="{obj.imvideo_by_userage.url}" download >скачать</a>')

    def download_img(self, obj):
        return mark_safe(f'<a href="{obj.cover_image.url}" download >скачать</a>')
    
    download_video.short_description = 'скачать видео'
    download_img.short_description = 'скачать изображения'


class SeasonalCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'create_at']
    search_fields = ['text']


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'apartment', 'create_at']
    list_display_links = list_display
    list_filter = ['user', 'apartment']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(apartment__owner=request.user)


admin.site.register(ViewStories, ViewStoriesAdmin)
admin.site.register(ComplaintStories)
admin.site.register(SeasonalComment, SeasonalCommentAdmin)
admin.site.register(Category)
admin.site.register(City)
