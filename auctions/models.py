from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

CATEGORIES=[

    ('Fashion', 'Fashion'),
    ('Toys', 'Toys'),
    ('Electronics', 'Electronics'),
    ('Home', 'Home'),
    ('Other', 'Other'),
]


class Listing(models.Model):
    title=models.CharField(max_length=32)
    seller=models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellers")
    description=models.CharField(max_length=1024)
    current_bid=models.DecimalField(decimal_places=2, max_digits=16)
    image_url=models.URLField(max_length=512, blank=True)
    category=models.CharField(choices=CATEGORIES, max_length=16, blank=True, default='Other')
    created_date=models.DateTimeField(default=timezone.now)
    listing_available=models.BooleanField(default=True)
    
class WatchList(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="watchlist")
    item=models.ForeignKey(Listing, on_delete=models.CASCADE, blank=False, related_name="users")
    
    def __str__(self):
        return f"{self.user} listed {self.item}"

class Bid(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name="bids")
    item=models.ForeignKey(Listing, on_delete=models.CASCADE, blank=False, related_name="buyers")
    amount=models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        return f"{self.user} bidded {self.amount} on {self.item}"

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=False, related_name="which_user")
    item=models.ForeignKey(Listing, on_delete=models.CASCADE, null=True, blank=False, related_name="comments") 
    comment=models.CharField(max_length=1024)
    comment_date=models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.user}  commented on {self.item.title} at {self.comment_date}"


