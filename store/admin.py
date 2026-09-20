from django.contrib import admin
from .models import (
    Category,
    Product,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
    Review,
)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Review)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'total_amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'user__username',
        'phone',
        'address',
    )

    ordering = (
        '-created_at',
    )
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
        'total_price',
    )

    search_fields = (
        'product__name',
        'order__user__username',
    )