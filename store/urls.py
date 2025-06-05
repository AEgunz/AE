from django.urls import path
from . import views

app_name = 'store' # Add app_name for namespacing

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'), # Category detail URL
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'), # New product detail URL
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-complete/', views.order_complete_placeholder, name='order_complete_placeholder'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('search/', views.search_view, name='search'),
    path('profile/', views.profile, name='profile'),

    # Custom Authentication URLs removed as django-allauth handles these.
    # Templates now point to:
    # {% url 'account_signup' %}
    # {% url 'account_login' %}
    # {% url 'account_logout' %}
]
