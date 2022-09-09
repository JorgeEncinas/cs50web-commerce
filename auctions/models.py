from unicodedata import name
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from matplotlib.pyplot import title
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy as gtlazy

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=280, null=False)
    imageURL = models.URLField(default="https://images.unsplash.com/photo-1613575573097-15f53a39267a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80")

    def __str__(self):
        return self.name

class Listing(models.Model):
    listingID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=180, null=False)
    description = models.CharField(max_length=800, null=False)
    startingBid = models.DecimalField(max_digits=14, decimal_places=2, null=False)
    imageURL = models.URLField(null=True, blank=True)
    categoryID = models.ForeignKey('Category', on_delete=models.SET_DEFAULT, related_name="category_listings", null=True, blank=True, default=0)
    ownerID = models.ForeignKey('User', on_delete=models.PROTECT, related_name="owned_listings")
    active = models.BooleanField(default = True)
    creationDatetime = models.DateTimeField(auto_now_add = True)
    users_watchlisted = models.ManyToManyField(User, related_name="watchlisted_listings")
    winnerID = models.ForeignKey('User',on_delete=models.PROTECT, related_name="listings_won", null=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    bidID = models.AutoField(primary_key=True)
    userID = models.ForeignKey('User', on_delete=models.PROTECT, related_name="user_bids")
    listingID = models.ForeignKey('Listing', on_delete=models.PROTECT, related_name="listing_bids")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    bidDatetime = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"""User {self.userID} bid {self.amount} on {self.listingID}"""

class Comment(models.Model):
    commentID = models.AutoField(primary_key=True)
    listingID = models.ForeignKey('Listing', on_delete=models.PROTECT, related_name="listing_comments")
    userID = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_comments")
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"""Comment with user {self.userID} at {self.timestamp}"""

class UserWatchlist(models.Model):
    userwatchlistID = models.AutoField(primary_key=True)
    userID = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_bookmarks")
    listingID = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="users_bookmarked")

    def __str__(self):
        return f"""User {self.userID} saved {self.listingID}"""

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'startingBid', 'imageURL', 'categoryID']
        widgets = {
            'description': Textarea(attrs={'cols':40, 'rows':10})
        }
        labels = {
            'title': gtlazy("Enter a public name for your listing:"),
            'description': gtlazy("Describe the object you're listing:"),
            'startingBid': gtlazy("Enter the starting bid for your listing:"),
            'imageURL': gtlazy("Enter a link to an image of your listing (Optional)"),
            'categoryID': gtlazy("Select the category that best fits your listing (Optional)")
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        labels = {
            'amount': gtlazy("Enter the amount you'll bid")
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class UserForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput,
        label="Create a password",
        max_length="50",
        required=True
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput,
        label="Confirm your password",
        max_length="50",
        required=True
    )


