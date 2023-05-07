from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:name>", views.category, name="category"),
    #path("categories/dog", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("listings", views.listing, name="listing"),
    path("listings/<int:listing_id>", views.listing, name="listings"),
]
