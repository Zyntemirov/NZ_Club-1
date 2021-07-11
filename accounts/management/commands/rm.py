from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        os.system('python manage.py makemigrations')
        os.system('python manage.py migrate')
