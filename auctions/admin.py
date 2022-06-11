from django.contrib import admin
from auctions.models import Category, Listing, Bid, Comment, User

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('categoryID', 'name')

@admin.action(description="Close selected listings")
def close_listings(modeladmin, request, queryset):
    queryset.update(active=False)

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    date_hierarchy = 'creationDatetime'
    list_display = ('listingID', 'title', 'startingBid', 'active', 'creationDatetime', 'ownerID', 'categoryID')
    fieldsets = (
        ('Identifying data', {
            'fields': ('listingID', 'title', 'startingBid')
        }),
        ('Metadata', {
            'fields': ('active', 'creationDatetime')
        }),
        ('Belongs to:', {
            'fields': ('ownerID', 'categoryID')
        }),
        ('Details given:', {
            'fields': ('description', 'imageURL')
        }),
    )
    actions = [close_listings]

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    date_hierarchy = 'bidDatetime'
    list_display = ('bidID', 'userID', 'listingID', 'amount', 'bidDatetime')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display = ('commentID', 'userID', 'comment', 'timestamp')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name')