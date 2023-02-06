# Generated by Django 4.1.3 on 2023-01-25 08:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0002_table_cloned_from"),
    ]

    operations = [
        migrations.CreateModel(
            name="Snapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("version", models.PositiveIntegerField()),
                ("data_rows", models.JSONField()),
                ("data_columns", models.JSONField()),
                ("column_stats", models.JSONField()),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_modified",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RemoveField(
            model_name="action",
            name="column",
        ),
        migrations.AddField(
            model_name="table",
            name="original_name",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="Column",
        ),
        migrations.AddField(
            model_name="snapshot",
            name="table",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.table"
            ),
        ),
    ]