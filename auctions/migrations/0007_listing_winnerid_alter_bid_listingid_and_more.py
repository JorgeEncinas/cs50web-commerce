# Generated by Django 4.0.5 on 2022-06-13 21:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_comment_listingid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='winnerID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='listings_won', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bid',
            name='listingID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='listing_bids', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='userID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_bids', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='comment',
            name='listingID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='listing_comments', to='auctions.listing'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='categoryID',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='category_listings', to='auctions.category'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='ownerID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owned_listings', to=settings.AUTH_USER_MODEL),
        ),
    ]
