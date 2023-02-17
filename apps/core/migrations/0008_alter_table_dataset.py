# Generated by Django 4.1.5 on 2023-02-16 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_alter_table_cloned_from_join_table_joined_from"),
    ]

    operations = [
        migrations.AlterField(
            model_name="table",
            name="dataset",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.dataset",
            ),
        ),
    ]