# Generated by Django 4.0.5 on 2022-08-03 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_listing_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image_url',
            field=models.URLField(blank=True, default='images/no_image.jpeg', max_length=512),
        ),
    ]