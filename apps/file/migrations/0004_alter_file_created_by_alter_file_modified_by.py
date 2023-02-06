# Generated by Django 4.1.3 on 2022-12-12 10:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("file", "0003_alter_file_created_by_alter_file_modified_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="file",
            name="modified_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_modified",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
