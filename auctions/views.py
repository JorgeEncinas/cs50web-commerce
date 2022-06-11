from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, Category, Listing, Bid, Comment, UserWatchlist, ListingForm, BidForm, UserForm


def index(request):
    listings_retrieved = Listing.objects.all()
    if listings_retrieved.count() > 0:
        listings_current_bids = []
        for listing in listings_retrieved:
            listings_current_bids.append(
                listing.listing_bids.all().aggregate(Max('amount'))
            )   
        return render(request, "auctions/index.html", {
            "listings": list(zip(listings_retrieved, listings_current_bids))
        })
    else:
        return render(request, "auctions/index.html", {
            "message":"There are no active listings at the moment."
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            if user_form.password != user_form.confirm_password:
                return render(request, "auctions/register.html", {
                    "message":"Passwords must match."
                })
            try:
                #user = User.objects.create_user(username, email, password)
                user = User.objects.create_user(
                    first_name=user_form.first_name,
                    last_name = user_form.last_name,
                    email=user_form.email,
                    username=user_form.username,
                    password=user_form.password,
                )
                user.save()
            except IntegrityError:
                return render(request, "auctions/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/register.html", {
                "message":"One of the fields you entered was not valid",
                "new_user_form":user_form
            })
    else:
        new_user_form = UserForm()
        return render(request, "auctions/register.html", {
            "new_user_form": new_user_form
        })

@login_required(login_url="login")
def new_listing(request):
    if request.method == "POST":
        listing_form = ListingForm(request.POST)
        if (listing_form.is_valid()):
            new_listing_data = listing_form.save(commit=False)
            user_req = request.user
            new_listing_data.ownerID = user_req
            new_listing_data.active = True
            if(new_listing_data.categoryID is None):
                new_listing_data.categoryID = 0
            new_listing_data.save()
            listing_created = Listing.objects.get(listingID=new_listing_data.pk)
            startingBidObject = Bid(request.user, listing_created, listing_created.startingbid)
            return render(request, "auctions/listing.html", {
                "message":"Listing saved successfully!",
                "listing": listing_created
            })
        else:
            return render(request, "auctions/new_listing.html",{
                "message":"We're sorry, one or more fields are not valid in your listing!",
                "listing_form":listing_form
            })
    else:
        listing_form = ListingForm()
        return render(request, "auctions/new_listing.html", {
            "listing_form": listing_form
        })

def get_listing(request, listingID):
    if request.method == "POST": #added to watchlist OR new bid
        listingID = request.POST.get("listingID")
        reason = request.POST.get("reason_code")
        if reason == "watchlist":
            user_bookmark = UserWatchlist.objects.get(listingID=listingID,
            userID=request.user.ID)
            if user_bookmark.count == 1:
                return render(request, "auctions/error404.html", {
                    "message":f"""You had already bookmarked listing #{listingID}. As punishment, you were sent to the 404 page!"""
                })
            else:
                return render(request, "auctions/")
        else: #reason is bidding
            listing_obj = Listing.objects.get(listingID=listingID)
            max_bid_obj = listing_obj.listing_bids.aggregate(Max('amount'))
            user_bid = request.POST.get("amount")
    else:
        #listingID = request.GET.get("listingID")
        listing_retrieved = Listing.objects.filter(listingID=listingID).first()
        if listing_retrieved is None:
            return render(request, "auctions/error404.html", {
                "message":f"""The listing you searched for, with code {listingID} was not found."""})
        else:
            current_max_bid = listing_retrieved.listing_bids.all().aggregate(Max('amount')).get("amount__max")
            try:
                bookmark_row = listing_retrieved.users_watchlisted.get(id=request.user.id)
                if bookmark_row.count() > 0:
                    already_bookmarked = True
            except User.DoesNotExist:
                already_bookmarked = False
            #Thanks to https://stackoverflow.com/a/813474 for this next line where I set the form's initial value
            bid_form = BidForm(initial={'amount':current_max_bid+1})
            return render(request, "auctions/listing.html", {
                "listing":listing_retrieved,
                "current_max_bid":current_max_bid,
                "user_already_bookmarked":already_bookmarked,
                "bid_form":bid_form
            })

@login_required(login_url="login")
def get_watchlist(request):
    userObject = request.user
    userWatchlisted = userObject.watchlisted_listings.all()
    if userWatchlisted.count() == 0:
        return render(request, "auctions/index.html", {
            "message":"You have no listings saved!"
        })
    else:
        return render(request, "auctions/index.html", {
            "listings":userWatchlisted
        })

def get_categories(request):
    categories = Category.objects.all()
    if categories.count() == 0:
        return render(request, "auctions/categories.html", {
            "message":"No categories found."
        })
    else:
        return render(request, "auctions/categories.html", {
            "categories":categories
        })

def get_category(request, categoryID):
    category_listings = Listing.objects.all().filter(categoryID=categoryID)
    category_retrieved = Category.objects.filter(categoryID=categoryID).first()
    if category_listings.count() == 0:
        return render(request, "auctions/index.html", {
            "message":f"""No listings for category <i>"{category_retrieved.name}"</i> were found :("""
        })
    else:
        listings_current_bids = []
        for listing in category_listings:
            listings_current_bids.append(
                listing.listing_bids.all().aggregate(Max('amount'))
            )
        return render(request, "auctions/index.html", {
            "listings": list(zip(category_listings, listings_current_bids))
        })