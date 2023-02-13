from django.urls import path, include
from .views import *


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout_user'),
    path('product/<slug:product_slug>/', ShowProduct.as_view(), name='show_product'),
    path('category/<slug:category_slug>/<int:category_id>/', ShowCategory.as_view(), name='show_category'),
    path('cart/', CartUser.as_view(), name='cart'),
    path('add_cart/<slug:product_slug>', AddToCart.as_view(), name='add_cart'),
    path('remove_cart/<slug:product_slug>', RemoveFromCart.as_view(), name='remove_cart'),
    path('change_qty/<slug:product_slug>', ChangeQtyProduct.as_view(), name='change_qty'),
]
