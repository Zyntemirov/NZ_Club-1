from django.apps import AppConfig


class VideoConfig(AppConfig):
    name = 'video'
    verbose_name = 'Видео'

    def ready(self):
        import video.signals

