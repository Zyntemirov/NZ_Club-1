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


admin.site.register(ViewStories, ViewStoriesAdmin)
admin.site.register(ComplaintStories)
