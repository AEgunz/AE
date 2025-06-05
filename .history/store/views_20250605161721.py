from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal # Import Decimal
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse # Import JsonResponse
from django.contrib import messages
from .models import Product, SliderImage, MobileSliderImage, Category, LogoCarouselItem, DeliveryCity, Order, OrderItem, ProductVariation, UserProfile
from .cart import Cart

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id] += 1
        else:
            cart[product_id] = 1

        request.session['cart'] = cart
        cart_count = sum(cart.values())
        return JsonResponse({'cart_count': cart_count})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def search_view(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Product.objects.filter(name__icontains=query)
    return render(request, 'store/search_results.html', {'query': query, 'results': results})

def home(request):
    products = Product.objects.filter(is_active=True)
    slider_images = SliderImage.objects.filter(is_active=True).order_by('order')
    mobile_slider_images = MobileSliderImage.objects.filter(is_active=True).order_by('order')
    categories = Category.objects.all()
    logo_carousel_items = LogoCarouselItem.objects.filter(is_active=True).order_by('order')
    context = {
        'products': products,
        'slider_images': slider_images,
        'mobile_slider_images': mobile_slider_images,
        'categories': categories,
        'logo_carousel_items': logo_carousel_items,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    variations = product.variations.filter(is_active=True)
    additional_images = product.additional_images.all().order_by('order')

    related_products = []
    if product.category:
        related_products = Product.objects.filter(category=product.category, is_active=True)\
                                          .exclude(id=product.id)\
                                          .order_by('?')[:4] # Get up to 4 random related products
                                          # Use '-created_at' or another field for consistent ordering if preferred

    context = {
        'product': product,
        'variations': variations,
        'additional_images': additional_images,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    variation_id = request.POST.get('variation_id')
    
    if not variation_id: # Convert empty string to None
        variation_id = None
    
    # For simplicity, we'll assume a quantity of 1 is always added.
    # A more complete implementation would get quantity from request.POST
    # e.g., quantity = int(request.POST.get('quantity', 1))
    # update_quantity = request.POST.get('update', 'false').lower() == 'true'
    
    # The cart.add method will need to be updated to accept variation_id
    cart.add(product=product, quantity=1, update_quantity=False, variation_id=variation_id)
    
    return JsonResponse({'status': 'ok', 'cart_total_items': len(cart)})

@require_POST # Ensure cart_remove is POST if using forms, or adjust if it's GET via link
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    variation_id = request.POST.get('variation_id') # Get from form if POST
    
    cart.remove(product, variation_id=variation_id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'cart_total_items': len(cart), 'cart_total_price': cart.get_total_price()})
    return redirect('store:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity')
    variation_id = request.POST.get('variation_id') # Get variation_id from form

    if quantity is not None:
        try:
            quantity = int(quantity)
            if quantity >= 0: # Allow 0 to remove
                cart.update(product=product, quantity=quantity, variation_id=variation_id)
            else:
                # Handle negative quantity if necessary, or ignore
                pass # Or return an error JsonResponse
        except ValueError:
            # Handle non-integer quantity if necessary
            pass # Or return an error JsonResponse
    
    # If this is called via AJAX (which it likely won't be from a simple form submit, but good practice)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_total_items': len(cart),
            'item_total_price': cart.cart.get(str(product_id), {}).get('price', 0) * cart.cart.get(str(product_id), {}).get('quantity', 0) if str(product_id) in cart.cart else 0,
            'cart_total_price': cart.get_total_price()
        })
    return redirect('store:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def checkout(request):
    cart = Cart(request)
    if not cart or len(cart) == 0: # Check if cart is empty
        return redirect('store:cart_detail') # Redirect to cart page if empty, maybe with a message

    cities = DeliveryCity.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        # Basic form validation (can be improved with Django Forms)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        city_id = request.POST.get('city')
        address = request.POST.get('address')
        email = request.POST.get('email') # Optional

        if not all([first_name, last_name, phone_number, city_id, address]):
            # Handle missing required fields - re-render form with an error message
            context = {
                'cart': cart,
                'cities': cities,
                'error_message': 'Please fill in all required fields.'
            }
            return render(request, 'store/checkout.html', context)

        try:
            selected_city = DeliveryCity.objects.get(id=city_id, is_active=True)
        except DeliveryCity.DoesNotExist:
            # Handle invalid city selection
            context = {
                'cart': cart,
                'cities': cities,
                'error_message': 'Invalid city selected.'
            }
            return render(request, 'store/checkout.html', context)

        # Create Order
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city_name=selected_city.name,
            delivery_city=selected_city,
            delivery_fee=selected_city.delivery_fee,
            total_amount=0 # Will be calculated
        )

        subtotal = Decimal('0.00')
        for item_data in cart: # Iterate through cart items
            product = item_data['product']
            quantity = item_data['quantity']
            price = item_data['price'] # Price at the time of adding to cart
            variation_id = item_data.get('variation_id') # Get variation_id if present in cart item
            
            variation_instance = None
            if variation_id:
                try:
                    variation_instance = ProductVariation.objects.get(id=variation_id, product=product)
                    # Optionally, adjust price if variation has an additional_price
                    # price += variation_instance.additional_price
                except ProductVariation.DoesNotExist:
                    pass # Or handle error: variation not found for this product

            OrderItem.objects.create(
                order=order,
                product=product,
                variation=variation_instance,
                price=price, # This price should ideally be the final price including variation adjustment
                quantity=quantity
            )
            subtotal += price * quantity # Ensure this 'price' is the final item price
        
        order.total_amount = subtotal + selected_city.delivery_fee
        order.save()

        # Clear the cart
        cart.clear()

        # Redirect to an order success page (to be created)
        # For now, let's redirect to home with a message or a simple HTTP response
        # return redirect('store:order_complete', order_id=order.id)
        return redirect('store:order_complete_placeholder') # Placeholder for now


    # GET request or form validation failed
    context = {
        'cart': cart,
        'cities': cities,
    }
    return render(request, 'store/checkout.html', context)

def order_complete_placeholder(request):
    # The path in render should be relative to the app's templates directory
    # or any globally configured template directory.
    # Since order_complete_placeholder.html is in store/templates/store/,
    # the path should be 'store/order_complete_placeholder.html'
    return render(request, 'store/order_complete_placeholder.html')

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Get all products in this category
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get all subcategories
    subcategories = category.children.all()
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    
    return render(request, 'store/category_detail.html', context)

# Authentication is handled by django-allauth

def profile(request):
    """View for user profile page."""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Process form submission
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('store:profile')
    else:
        # Initialize form with current profile data
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'user': request.user,
        'profile': user_profile,
        'form': form,
        'profile_user': request.user,  # For template title
    }
    
    return render(request, 'store/profile.html', context)
