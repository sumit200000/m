from django.urls import path
from . import views
from .views import add_to_cart
from .views import user_login
from .views import user_logout,register

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.product_listing, name='product_listing'),
    path('books/<int:id>/', views.product_detail, name='product_detail'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy/', views.buy_product, name='buy_product'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('profile/', views.profile, name='profile'),
    path('order_history/', views.order_history, name='order_history'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('complete_order/', views.complete_order, name='order_complete'),
    
  
]
