from django.contrib import admin

from apps.core.models import (
    Dataset,
    Table,
    Snapshot,
)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    pass


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    pass
