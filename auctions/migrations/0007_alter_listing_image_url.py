# Generated by Django 4.0.5 on 2022-08-03 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_listing_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image_url',
            field=models.URLField(blank=True, max_length=512),
        ),
    ]