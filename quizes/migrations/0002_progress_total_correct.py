# Generated by Django 5.1.7 on 2025-05-14 22:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="progress",
            name="total_correct",
            field=models.IntegerField(default=0),
        ),
    ]
