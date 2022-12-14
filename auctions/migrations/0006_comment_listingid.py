# Generated by Django 4.0.5 on 2022-06-12 00:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_listing_users_watchlisted'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='listingID',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='listing_comments', to='auctions.listing'),
            preserve_default=False,
        ),
    ]
