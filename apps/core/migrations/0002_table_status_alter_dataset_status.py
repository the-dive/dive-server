# Generated by Django 4.1.3 on 2022-12-01 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="table",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("uploaded", "Uploaded"),
                    ("extracted", "Extracted"),
                ],
                default="pending",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="dataset",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("uploaded", "Uploaded"),
                    ("extracted", "Extracted"),
                ],
                default="pending",
                max_length=50,
            ),
        ),
    ]
