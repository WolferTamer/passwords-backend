# Generated by Django 5.1.2 on 2024-11-11 23:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_account_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='account',
            constraint=models.UniqueConstraint(fields=('site', 'owner'), name='unique_site_owner_combination'),
        ),
    ]