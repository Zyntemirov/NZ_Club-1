from django.contrib import admin
from seasonal.models import *
from adminsortable2.admin import SortableAdminMixin
from django.utils.safestring import mark_safe
from django.http.response import HttpResponseRedirect


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
    fields = (('image', 'download_img'), 'apartment')
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
    list_display = ['id', 'entry_date', 'exit_date', 'room', 'phone', 'accept']
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
    change_form_template = 'admin/changeform.html'
    save_on_top = True

    def response_change(self, request, obj):
        if request.user.is_superuser:
            apartment = SeasonalApartment.objects.get(id=obj.id)
            if 'approve' in request.POST:
                apartment.is_checked = True
                apartment.save()
                self.message_user(request, 'Видео активна')
                return HttpResponseRedirect('.')
            elif 'disapprove' in request.POST:
                apartment.is_checked = False
                apartment.save()
                self.message_user(request, 'Видео отключен')
                return HttpResponseRedirect('.')
        return super().response_change(request, obj)

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


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['status', 'name', 'address', 'phone', 'category', 'city',]
    list_display_links = list_display
    readonly_fields = ['create_at',]
    search_fields = ['name', ]
    list_filter = ['owner__username']
    change_form_template = 'admin/RequestChangeForm.html'
    save_on_top = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.order_by('status')
        return qs.filter(owner=request.user)

    def response_change(self, request, obj):
        if request.user.is_superuser:
            req = Request.objects.get(id=obj.id)
            if 'approve' in request.POST:
                req.status = '2'
                req.save()
                apartment = SeasonalApartment.objects.create(name=obj.name,
                                        description=obj.description,
                                        address=obj.address,
                                        phone=obj.phone,
                                        video_by_user=obj.video_by_user,
                                        category=obj.category,
                                        city=obj.city,
                                        cover_image=obj.cover_image,
                                        owner=obj.owner
                                        )
                images = ApartmentRequestImage.objects.filter(apartment__id=obj.id)
                if images:
                    for image in images:
                        ad_image = ApartmentImage(apartment=apartment, image=image)
                        ad_image.save()
                    images.delete()
                self.message_user(request, 'Видео создан')
                return HttpResponseRedirect('.')
            elif 'disapprove' in request.POST:
                req.status = '1'
                req.save()
                self.message_user(request, 'Запрос откланен')
                return HttpResponseRedirect('.')
        return super().response_change(request, obj)

    def get_owner_region(self, obj):
        return f'{obj.owner.profile.get_region_display()}'

    get_owner_region.short_description = 'Регион'

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['name', 'description', 'address', 'phone', 'video_by_user', 'category', 'city', 'cover_image', 'owner', 'status', 'create_at']
        else:
            return ['name', 'description', 'address', 'phone', 'video_by_user', 'category', 'city', 'cover_image', 'owner', 'create_at']
    


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
