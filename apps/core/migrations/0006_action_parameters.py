# Generated by Django 4.1.3 on 2023-02-09 08:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_remove_action_parameters_action_action_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="parameters",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=200), default=[], size=None
            ),
            preserve_default=False,
        ),
    ]