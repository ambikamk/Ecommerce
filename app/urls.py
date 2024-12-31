from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.home,name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('delete-from-cart/<int:cart_item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('search/', views.search_products, name='search_products'),
    path('cart/increment/<int:cart_item_id>/', views.increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:cart_item_id>/', views.decrement_quantity, name='decrement_quantity'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)