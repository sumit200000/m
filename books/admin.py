from django.contrib import admin
from .models import Book, Cart, Review, Order, OrderItem, Category, Wishlist
from .views import update_order_status

# Define custom actions for OrderAdmin

def make_shipped(modeladmin, request, queryset):
    for order in queryset:
        update_order_status(order, 'Shipped')
make_shipped.short_description = "Mark selected orders as shipped"


def make_delivered(modeladmin, request, queryset):
    for order in queryset:
        update_order_status(order, 'Delivered')
make_delivered.short_description = "Mark selected orders as delivered"

# Define ModelAdmin classes
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'status')
    actions = [make_shipped, make_delivered]

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'featured')
    list_filter = ('category', 'featured')
    search_fields = ('title', 'description')

# Register models with corresponding ModelAdmin classes
admin.site.register(Book, BookAdmin)
admin.site.register(Cart)
admin.site.register(Review)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(Wishlist)

# books/admin.py




