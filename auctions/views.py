from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.db.models import Max
from operator import attrgetter

class NewForm(forms.ModelForm):
    class Meta:
        model=Listing
        fields = ('title', 'current_bid', 'description', 'image_url', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'current_bid': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min':0.01, 'style': 'width:200px'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm'}),
            'image_url': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'category': forms.Select(attrs={'class': 'form-control form-control-sm'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model=Bid
        fields = ('amount',)
        widgets = {
            'amount': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'type':'number', 'style':'width:200px'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields = ('comment',)
        widgets = {
                'comment': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'cols':65, 'rows':5, 'style':'width:500px; margin-bottm:20px; '}),
        }

        labels = {
                'comment': ""
        }
        


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html",{
        'listings': Listing.objects.all(),
    })


def login_view(request):

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            request.session["username"]=username
            request.session["password"]=password
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
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    if not request.user.is_authenticated:
        return listing_user_not_logged(request, listing_id)
    else:
        return listing_user_logged(request, listing_id)

def listing_user_not_logged(request, listing_id):
    listing=Listing.objects.get(pk=listing_id)
    
    comments=Comment.objects.filter(item=listing)

    all_max_bid = Bid.objects.filter(item=listing).aggregate(Max('amount'))

    bid_count = Bid.objects.filter(item=listing).count()
    
    return render(request, "auctions/listing.html", {
        "id": listing_id,
        "title": listing.title,
        "description": listing.description,
        "seller": listing.seller,
        "start_bid" : listing.current_bid,
        "category": listing.category,
        "image_url" : listing.image_url,
        "bid_count": bid_count,
        "available": listing.listing_available,
        "comments": comments,
    })


def listing_user_logged(request, listing_id):
    listing=Listing.objects.get(pk=listing_id)
    user1 = User.objects.get(username=request.user)
    
    comments=Comment.objects.filter(item=listing)

    msg = "no bid"
    if request.method == "POST":
        #add to watchlist
        if request.POST.get("button")=="watch_add":
            if not user1.watchlist.filter(item=listing):
                listing=Listing.objects.get(pk=listing_id)
                watchlist = WatchList(user=user1, item=listing)
                watchlist.save()
            else:
                WatchList.objects.filter(user=user1, item=listing).delete()
        
        #remove from watchlist
        if request.POST.get("button")=="watch_remove":
            if user1.watchlist.filter(item=listing):
                WatchList.objects.filter(user=user1, item=listing).delete()

        #close auction
        if request.POST.get("button")=="close":
            listing.listing_available = False
            listing.save()
        
        #add bid
        if request.POST.get("add_bid"):
            
            listing=Listing.objects.get(pk=listing_id)
            user1 = User.objects.get(username=request.user)
            value=request.POST.get("add_bid")

            bid_count = Bid.objects.filter(item=listing).count()

            if (float(value) > listing.current_bid or ((float(value) == listing.current_bid) and (bid_count == 0))):
                msg = "succes"
                bid = Bid()
                bid.user = user1
                bid.amount = value
                bid.item = listing
                listing.current_bid = value;
                listing.save()
                bid.save()
            else:
                msg = "not succes"
    
        #add comment
        if request.POST.get("button")=="add_comment":
            user = User.objects.get(username=request.user)
            cform = CommentForm(request.POST)
            if cform.is_valid():
                comment = cform.save(commit=False)
                comment.user = user
                comment.item = listing
                #Comment.objects.all().delete()
                comment.save()


    is_seller = False
    #check the logged user and the seller are same
    if (listing.seller == user1):
        is_seller = True

    #return the max bid value of the user for this item     
    user_max_bid = Bid.objects.filter(user=user1, item=listing).aggregate(Max('amount'))
    #return the max bid of any user for this item
    all_max_bid = Bid.objects.filter(item=listing).aggregate(Max('amount'))

    bid_count = Bid.objects.filter(item=listing).count()
    is_user = None
    is_user_bid_max = False

    
    if ((user_max_bid == all_max_bid) and (bid_count != 0)):
        is_user = "your bid is the current bid"
        is_user_bid_max = True

    bid1 = None
    if  Bid.objects.filter(user=user1, item=listing):
        bid1 = max(Bid.objects.filter(user=user1, item=listing), key=attrgetter('amount'))

    watchlist_all = WatchList.objects.filter(user=user1, item=listing)
    watchlist2 = watchlist_all
    
    return render(request, "auctions/listing.html", {
        "id": listing_id,
        "title": listing.title,
        "description": listing.description,
        "seller": listing.seller,
        "start_bid" : listing.current_bid,
        "category": listing.category,
        "image_url" : listing.image_url,
        "bid": bid1,
        "watchlist": watchlist2,
        "msg": msg,
        "bid_count": bid_count,
        "is_user": is_user,
        "available": listing.listing_available,
        "is_seller_logged": is_seller,
        "is_user_bid_max": is_user_bid_max,
        "cform": CommentForm,
        "comments": comments,
    })


def create(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        form = NewForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
            "form": form
            })
    else:
        return render(request, "auctions/create.html", {
        "form": NewForm()
        })

def categories(request):
    return render(request, "auctions/categories.html",{
        "fashion": CATEGORIES[0][0],
        "toys": CATEGORIES[1][0],
        "electronics": CATEGORIES[2][0],
        "home": CATEGORIES[3][0],
        "other": CATEGORIES[4][0],
    })

def category(request, name):
    listings = Listing.objects.filter(category=name)
    return render(request, "auctions/category.html",{
        "listings": listings,
    })

def watchlist(request):
    user1 = User.objects.get(username=request.user)
    return render(request, "auctions/watchlist.html",{
        "watchlist": WatchList.objects.filter(user=user1),
    })
