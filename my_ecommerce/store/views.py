from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal # Import Decimal
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse # Import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, SliderImage, MobileSliderImage, Category, LogoCarouselItem, DeliveryCity, Order, OrderItem, ProductVariation, UserProfile, ProductRating
from .cart import Cart
from .forms import UserProfileForm
from .utils import send_order_notification_to_admin
from .models import ContactMessage
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import Product, Category

from django.shortcuts import get_object_or_404, render
from .models import Category, Product
from .forms import ProductFilterForm

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = Category.objects.filter(parent=category)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get all categories for the filter
    all_categories = Category.objects.all()
    
    # Get unique colors from product variations
    color_choices = []
    product_variations = ProductVariation.objects.filter(product__category=category, is_active=True)
    if product_variations.exists():
        color_choices = list(set([(v.color_name, v.color_name) for v in product_variations if v.color_name]))
    
    # Get unique brands from products
    brand_choices = []
    if products.exists():
        brand_choices = list(set([(p.brand, p.brand) for p in products if p.brand]))
    
    # Create the filter form with dynamic choices
    form = ProductFilterForm(
        request.GET or None,
        category_queryset=all_categories,
        color_choices=color_choices,
        brand_choices=brand_choices
    )
    
    if form.is_valid():
        # Price filtering
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        # Category filtering
        filter_category = form.cleaned_data.get('category')
        
        # Color filtering
        color = form.cleaned_data.get('color')
        
        # Size filtering (for future implementation)
        size = form.cleaned_data.get('size')
        
        # Brand filtering (for future implementation)
        brand = form.cleaned_data.get('brand')
        
        # Rating filtering (for future implementation)
        rating = form.cleaned_data.get('rating')
        
        # Sorting
        order_by = form.cleaned_data.get('order_by')
        
        # Apply filters
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if filter_category:
            # If a subcategory is selected, filter by it
            products = products.filter(category=filter_category)
        if color:
            # Filter by color using variations
            product_ids = ProductVariation.objects.filter(
                product__category=category,
                color_name=color,
                is_active=True
            ).values_list('product_id', flat=True)
            products = products.filter(id__in=product_ids)
            
        # Size filtering
        size = form.cleaned_data.get('size')
        if size:
            product_ids = ProductVariation.objects.filter(
                product__category=category,
                size=size,
                is_active=True
            ).values_list('product_id', flat=True)
            products = products.filter(id__in=product_ids)
            
        # Brand filtering
        brand = form.cleaned_data.get('brand')
        if brand:
            products = products.filter(brand=brand)
            
        # Rating filtering
        rating = form.cleaned_data.get('rating')
        if rating:
            # Convert rating to integer
            try:
                rating_value = int(rating)
                product_ids = ProductVariation.objects.filter(
                    product__category=category,
                    rating__gte=rating_value,
                    is_active=True
                ).values_list('product_id', flat=True)
                products = products.filter(id__in=product_ids)
            except (ValueError, TypeError):
                # Handle invalid rating value
                pass
        if order_by:
            products = products.order_by(order_by)

    context = {
        'category': category,
        'categories': Category.objects.filter(parent=None),
        'subcategories': subcategories,
        'products': products,
        'form': form,
    }

    return render(request, 'store/category_detail.html', context)



def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    color = request.GET.get('color')

    if category:
        products = products.filter(category__name=category)
    if color:
        products = products.filter(color=color)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'selected_color': color,
    }
    return render(request, 'store/product_list.html', context)

def about_us(request):
    return render(request, 'store/about_us.html')

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

def contact_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        name = f"{first_name} {last_name}"
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=f"Phone: {phone}",  # حطينا رقم الهاتف كـ subject مؤقتًا
            message=message
        )

        # Compose the email content
        subject = f"📩 New Message from {name} - AE Piscine"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = ['dbdddf76da-bffa6c+user1@inbox.mailtrap.io']

        text_content = f"New message from {name} - {email} - {phone}\n\n{message}"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <style>
            body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            padding: 20px;
            color: #333;
            }}
            .container {{
            max-width: 600px;
            margin: auto;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 30px;
            }}
            .header {{
            text-align: center;
            margin-bottom: 25px;
            }}
            .header h2 {{
            color: #0073e6;
            margin: 0;
            }}
            .info p {{
            font-size: 16px;
            margin: 8px 0;
            }}
            .info strong {{
            color: #005bb5;
            }}
            .message-box {{
            background: #f0f0f0;
            padding: 15px;
            margin-top: 20px;
            border-left: 5px solid #0073e6;
            white-space: pre-wrap;
            }}
            .footer {{
            margin-top: 30px;
            font-size: 13px;
            color: #888;
            text-align: center;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
            <h2>📨 New Contact Form Message</h2>
            </div>
            <div class="info">
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            </div>
            <div class="message-box">
            {message}
            </div>
            <div class="footer">
            This message was sent from the contact form on AE Piscine's website.
            </div>
        </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    return render(request, 'store/contact.html')

def search_view(request):
    query = request.GET.get('q')
    results = []
    
    if query:
        results = Product.objects.filter(name__icontains=query, is_active=True)
        
        # Get all categories for the filter
        all_categories = Category.objects.all()
        
        # Get unique colors from product variations
        color_choices = []
        product_variations = ProductVariation.objects.filter(product__in=results, is_active=True)
        if product_variations.exists():
            color_choices = list(set([(v.color_name, v.color_name) for v in product_variations if v.color_name]))
        
        # Get unique brands from products
        brand_choices = []
        if results.exists():
            brand_choices = list(set([(p.brand, p.brand) for p in results if p.brand]))
        
        # Create the filter form with dynamic choices
        form = ProductFilterForm(
            request.GET or None,
            category_queryset=all_categories,
            color_choices=color_choices,
            brand_choices=brand_choices
        )
        
        if form.is_valid():
            # Price filtering
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            
            # Category filtering
            filter_category = form.cleaned_data.get('category')
            
            # Color filtering
            color = form.cleaned_data.get('color')
            
            # Size filtering (for future implementation)
            size = form.cleaned_data.get('size')
            
            # Brand filtering (for future implementation)
            brand = form.cleaned_data.get('brand')
            
            # Rating filtering (for future implementation)
            rating = form.cleaned_data.get('rating')
            
            # Sorting
            order_by = form.cleaned_data.get('order_by')
            
            # Apply filters
            if min_price is not None:
                results = results.filter(price__gte=min_price)
            if max_price is not None:
                results = results.filter(price__lte=max_price)
            if filter_category:
                results = results.filter(category=filter_category)
            if color:
                # Filter by color using variations
                product_ids = ProductVariation.objects.filter(
                    product__in=results,
                    color_name=color,
                    is_active=True
                ).values_list('product_id', flat=True)
                results = results.filter(id__in=product_ids)
                
            # Size filtering
            size = form.cleaned_data.get('size')
            if size:
                product_ids = ProductVariation.objects.filter(
                    product__in=results,
                    size=size,
                    is_active=True
                ).values_list('product_id', flat=True)
                results = results.filter(id__in=product_ids)
                
            # Brand filtering
            brand = form.cleaned_data.get('brand')
            if brand:
                results = results.filter(brand=brand)
                
            # Rating filtering
            rating = form.cleaned_data.get('rating')
            if rating:
                # Convert rating to integer
                try:
                    rating_value = int(rating)
                    product_ids = ProductVariation.objects.filter(
                        product__in=results,
                        rating__gte=rating_value,
                        is_active=True
                    ).values_list('product_id', flat=True)
                    results = results.filter(id__in=product_ids)
                except (ValueError, TypeError):
                    # Handle invalid rating value
                    pass
            if order_by:
                results = results.order_by(order_by)
        
        context = {
            'query': query,
            'results': results,
            'form': form,
        }
    else:
        context = {
            'query': query,
            'results': results,
        }
    
    return render(request, 'store/search_results.html', context)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})
    
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
    
    # Get product ratings
    ratings = product.ratings.all()
    avg_rating = 0
    if ratings.exists():
        avg_rating = sum(rating.rating for rating in ratings) / len(ratings)

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
        'ratings': ratings,
        'avg_rating': avg_rating,
    }
    return render(request, 'store/product_detail.html', context)

@require_POST
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    rating_value = request.POST.get('rating')
    comment = request.POST.get('comment', '')
    
    if not rating_value:
        messages.error(request, 'Please select a rating.')
        return redirect('store:product_detail', product_slug=product.slug)
    
    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            raise ValueError("Rating must be between 1 and 5")
    except (ValueError, TypeError):
        messages.error(request, 'Invalid rating value.')
        return redirect('store:product_detail', product_slug=product.slug)
    
    # Check if user is authenticated
    if request.user.is_authenticated:
        # Check if user has already rated this product
        existing_rating = ProductRating.objects.filter(product=product, user=request.user).first()
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.comment = comment
            existing_rating.save()
            messages.success(request, 'Your rating has been updated.')
        else:
            # Create new rating
            ProductRating.objects.create(
                product=product,
                user=request.user,
                rating=rating_value,
                comment=comment
            )
            messages.success(request, 'Thank you for rating this product!')
    else:
        # Anonymous rating
        ip_address = request.META.get('REMOTE_ADDR')
        # Check if this IP has already rated this product
        existing_rating = ProductRating.objects.filter(product=product, ip_address=ip_address, user__isnull=True).first()
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.comment = comment
            existing_rating.save()
            messages.success(request, 'Your rating has been updated.')
        else:
            # Create new rating
            ProductRating.objects.create(
                product=product,
                rating=rating_value,
                comment=comment,
                ip_address=ip_address
            )
            messages.success(request, 'Thank you for rating this product!')
    
    return redirect('store:product_detail', product_slug=product.slug)

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
    
    # Initialize initial data dictionary
    initial_data = {}
    
    # If user is authenticated, pre-fill form with profile data
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone_number': profile.phone_number,
                'address': profile.address_line_1,
                'city_name': profile.city
            }
        except:
            # If profile doesn't exist or there's an error, continue without pre-filling
            pass

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
        
        # Send notification email to admin
        send_order_notification_to_admin(order)

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
        'initial_data': initial_data,
    }
    return render(request, 'store/checkout.html', context)

def order_complete_placeholder(request):
    # The path in render should be relative to the app's templates directory
    # or any globally configured template directory.
    # Since order_complete_placeholder.html is in store/templates/store/,
    # the path should be 'store/order_complete_placeholder.html'
    return render(request, 'store/order_complete_placeholder.html')

# This function has been consolidated above

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
