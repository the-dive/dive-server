# Generated by Django 4.1.3 on 2022-12-21 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_action_created_by_alter_action_modified_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='preview_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]