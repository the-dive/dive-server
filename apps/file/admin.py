from django.contrib import admin

from apps.file.models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
