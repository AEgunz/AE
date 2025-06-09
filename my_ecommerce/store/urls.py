from . import views
from django.urls import path, include



app_name = 'store' 

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/rate/', views.rate_product, name='rate_product'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-complete/', views.order_complete_placeholder, name='order_complete_placeholder'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('search/', views.search_view, name='search'),
    path('profile/', views.profile, name='profile'),
    path('about-us/', views.about_us, name='about_us'),    
    path('contact/', views.contact_view, name='contact'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail')
]

    
    

    # Custom Authentication URLs removed as django-allauth handles these.
    # Templates now point to:
    # {% url 'account_signup' %}
    # {% url 'account_login' %}
    # {% url 'account_logout' %}
