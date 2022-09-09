from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max

from .models import User, Category, Listing, Bid, Comment, ListingForm, BidForm, UserForm, CommentForm


def index(request):
    listings_retrieved = Listing.objects.filter(active=True).order_by('-creationDatetime')
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
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            username = user_form.cleaned_data['username']
            email = user_form.cleaned_data['email']
            password = user_form.cleaned_data['password']
            confirm_password = user_form.cleaned_data['confirm_password']
            if password != confirm_password:
                return render(request, "auctions/register.html", {
                    "message":"Passwords must match."
                })
            try:
                #user = User.objects.create_user(username, email, password)
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password
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
            startingBidObject = Bid(userID=request.user, listingID=listing_created, amount=listing_created.startingBid)
            startingBidObject.save()
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
    listing_retrieved = Listing.objects.filter(listingID=listingID).first()
    if listing_retrieved is None:
        return render(request, "auctions/error404.html", {
            "message":f"""The listing you searched for, with code {listingID} was not found."""})
    else:
        return go_to_listing(request=request, message="", listing=listing_retrieved)

@login_required(login_url="login")
def get_watchlist(request):
    userObject = request.user
    userWatchlisted = userObject.watchlisted_listings.all()
    if userWatchlisted.count() == 0:
        return render(request, "auctions/index.html", {
            "message":"You have no listings saved!"
        })
    else:
        listings_current_bids = []
        for listing in userWatchlisted:
            listings_current_bids.append(
                listing.listing_bids.all().aggregate(Max('amount'))
            )   
        return render(request, "auctions/index.html", {
            "listings":list(zip(userWatchlisted, listings_current_bids))
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
    category_listings = Listing.objects.all().filter(categoryID=categoryID, active=True).order_by('-creationDatetime')
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

#Made new function for this to be able to use login's "next" redirection functionality.
@login_required(login_url="login")
def change_watchlist(request, listingID):
    if request.method == "POST":
        user = request.user
        try:
            listing = user.watchlisted_listings.get(listingID=listingID)
            #Thanks to https://stackoverflow.com/a/6333198 showing how to remove in ManyToMany
            user.watchlisted_listings.remove(listing)
            return go_to_listing(request, listing=listing, message="Listing removed from your watchlist!")
        except Listing.DoesNotExist:
            try:
                TBA_listing = Listing.objects.get(listingID=listingID)
                user.watchlisted_listings.add(TBA_listing)
                return go_to_listing(request=request, message="Listing added successfully to your watchlist", listing=TBA_listing)
            except Listing.DoesNotExist:
                return render(request, "auctions/index.html", {
                    "message":"Listing was no longer found. It may have been deleted entirely."
                })
    else:
        return redirect("get_listing", listingID=listingID)

#Did it on separate view to be able to get user back to where they want to be.
@login_required(login_url="login")
def make_bid(request, listingID):
    #Thanks to https://stackoverflow.com/a/3644910 for showing me how to check if user is authenticated.
    if request.method == "POST": #added to watchlist OR new bid
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            try:
                listing = Listing.objects.get(listingID=listingID)
                if listing.active == False:
                    return go_to_listing(request=request, listing=listing, message="Listing already closed.")
            except Listing.DoesNotExist:
                return render(request, "auctions/index.html", {
                    "message":"Listing has been deleted."
                })
            current_max_bid = listing.listing_bids.all().aggregate(Max('amount')).get("amount__max")
            bid_form_amount = bid_form.cleaned_data["amount"]
            if bid_form_amount > current_max_bid or (bid_form_amount == listing.startingBid and listing.startingBid == current_max_bid):
                bid_data = bid_form.save(commit=False)
                bid_data.userID = request.user
                bid_data.listingID = listing
                bid_data.save()
            else:
                return go_to_listing(request=request, listing=listing, message="Bid amount is not higher than the current highest bid")
            return go_to_listing(request=request, listing=listing, message="Bid successfully!")
    else:
        return redirect("get_listing", listingID=listingID)

@login_required(login_url="login")
def close_auction(request, listingID):
    if request.method == "POST":
        #Change listing from active = 1 to active = 0
        try:
            listing = Listing.objects.get(listingID=listingID)
            if listing.ownerID == request.user:
                #Thanks to https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django for showing how to actually get the object in select MAX.
                winning_bid = Bid.objects.filter(listingID=listing).order_by("-amount").first()
                if winning_bid is not None:
                    listing.winnerID = winning_bid.userID
                    listing.active = 0
                    listing.save()
                else:
                    return go_to_listing(request=request, listing=listing, message="No bid found to close the auction.")
            else:
                return go_to_listing(request=request, listing=listing, message="You're not the owner of this listing")
        except Listing.DoesNotExist or User.DoesNotExist:
            return render(request, "auctions/index.html", {
                "message":"Listing does not exist anymore."
            })
        return go_to_listing(request=request, listing=listing, message="You've closed the auction!")
    else:
        return redirect("get_listing", listingID=listingID)

def get_max_bid_amount(listing):
    return listing.listing_bids.all().aggregate(Max('amount')).get("amount__max")

def go_to_listing(request, message, listing):
    current_max_bid = get_max_bid_amount(listing)
    try:
        bookmark_row = listing.users_watchlisted.get(id=request.user.id)
        already_bookmarked = True
    except User.DoesNotExist:
        already_bookmarked = False
    #Thanks to https://stackoverflow.com/a/813474 for this next line where I set the form's initial value
    bid_form = BidForm(initial={'amount':current_max_bid+1})
    if listing.active == False:
        bid_message=""
        if listing.winnerID == request.user:
            message += "\nYou won the auction!"
        else:
            message += "\n We're sorry, somebody else won the auction"
    else:
        highest_bid = Bid.objects.filter(listingID=listing).order_by("-amount").first()
        if highest_bid is not None:
            if highest_bid.userID == request.user:
                bid_message = "You're the current highest bid!"
            else:
                bid_message = "You're not the highest bidder right now"
        else:
            bid_message = "Something unexpected happened getting the bid data."
    comment_form = CommentForm()
    comments = Comment.objects.filter(listingID=listing.listingID)
    return render(request, "auctions/listing.html", {
        "message":message,
        "listing":listing,
        "bid_form":bid_form,
        "user_already_bookmarked":already_bookmarked,
        "current_max_bid":current_max_bid,
        "comments":comments,
        "comment_form":comment_form,
        "bid_message":bid_message
    })

@login_required(login_url="login")
def new_comment(request, listingID):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(listingID=listingID)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment_data = comment_form.save(commit=False)
                comment_data.userID = request.user
                comment_data.listingID = listing
                comment_data.save()
                return go_to_listing(request=request, listing=listing, message="Comment made successfully!")
            else:
                return go_to_listing(request=request, listing=listing, message="Comment data is not valid.")
        except Listing.DoesNotExist:
            return render(request, "auctions/index.html", {
                "message":"Listing does not exist anymore."
            })            
    else:
        return go_to_listing(request=request, listing=listingID, message="You can't do that")