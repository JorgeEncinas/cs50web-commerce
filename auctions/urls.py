from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("categories", views.get_categories, name="categories"),
    path("watchlist", views.get_watchlist, name="watchlist"),
    path("get_listing/<int:listingID>", views.get_listing, name="get_listing"),
    path("get_category/<int:categoryID>", views.get_category, name="get_category")
]
