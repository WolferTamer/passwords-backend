# Generated by Django 5.1.2 on 2024-11-28 01:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_emailotpdevice'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailotpdevice',
            name='confirmed',
        ),
        migrations.RemoveField(
            model_name='emailotpdevice',
            name='name',
        ),
        migrations.AlterField(
            model_name='emailotpdevice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]