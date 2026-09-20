from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path(
    'wishlist/add/<int:product_id>/',
    views.add_to_wishlist,
    name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path(
    'wishlist/remove/<int:item_id>/',
    views.remove_from_wishlist,
    name='remove_from_wishlist'),
    path(
    'product/<int:product_id>/',
    views.product_detail,
    name='product_detail'),
    path(
    'checkout/',
    views.checkout,
    name='checkout'),
    path(
    'order-success/<int:order_id>/',
    views.order_success,
    name='order_success'
),
    path(
    'my-orders/',
    views.my_orders,
    name='my_orders'
),
    path(
    'shop/',
    views.shop,
    name='shop'
),
    path(
    'order/<int:order_id>/',
    views.order_detail,
    name='order_detail'
),
    path(
    'order/<int:order_id>/cancel/',
    views.cancel_order,
    name='cancel_order'
),
path(
    'product/<int:product_id>/',
    views.product_detail,
    name='product_detail'
),
    path(
    'product/<int:product_id>/review/',
    views.add_review,
    name='add_review'
),

]