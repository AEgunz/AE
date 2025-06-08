from decimal import Decimal # Ensure Decimal is imported
from django.db import models
from django.urls import reverse # Import reverse for get_absolute_url
from django.utils.text import slugify # Import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

import os


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Optional image for the category.")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', help_text="Select a parent category to make this a subcategory.")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure unique constraint for name within the same parent, or globally if parent is None
        # unique_together = ('parent', 'name') # Optional: if you want names to be unique only under a specific parent
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True) # Added category
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True) # Added slug
    short_description = models.TextField(blank=True, null=True, help_text="A brief summary shown on product detail page under the title.") # Changed to TextField
    description = models.TextField(help_text="Full product description.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) # Added is_active

    class Meta: # Added Meta class for ordering
        ordering = ['-created_at']

    def save(self, *args, **kwargs): # Added save method for slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'product_slug': self.slug})

    def delete(self, *args, **kwargs):
        # Suprimi l'image men storage
        if self.image:
            storage, path = self.image.storage, self.image.path
            super().delete(*args, **kwargs)
            storage.delete(path)
        else:
            super().delete(*args, **kwargs)
    

class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    title = models.CharField(max_length=200, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    link_url = models.URLField(max_length=200, blank=True, null=True, help_text="Optional: URL the slide links to.")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the slide appears.")
    is_active = models.BooleanField(default=True, help_text="Only active slides will be displayed.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return self.title if self.title else f"Slide {self.id}"

class MobileSliderImage(models.Model):
    image = models.ImageField(upload_to='mobile_slider_images/')
    title = models.CharField(max_length=200, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    link_url = models.URLField(max_length=200, blank=True, null=True, help_text="Optional: URL the slide links to.")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the slide appears.")
    is_active = models.BooleanField(default=True, help_text="Only active slides will be displayed.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mobile Slider Image"
        verbose_name_plural = "Mobile Slider Images"
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return self.title if self.title else f"Mobile Slide {self.id}"

class LogoCarouselItem(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the brand/logo (for internal reference or alt text)")
    logo_image = models.ImageField(upload_to='logo_carousel/')
    link_url = models.URLField(max_length=200, blank=True, null=True, help_text="Optional: URL the logo links to.")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the logo appears.")
    is_active = models.BooleanField(default=True, help_text="Only active logos will be displayed.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Logo Carousel Item"
        verbose_name_plural = "Logo Carousel Items"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class DeliveryCity(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the city")
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, help_text="Delivery fee for this city")
    is_active = models.BooleanField(default=True, help_text="Whether delivery is currently available to this city")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delivery City"
        verbose_name_plural = "Delivery Cities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (+${self.delivery_fee})"

class Order(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city_name = models.CharField(max_length=100) # Store city name at time of order
    delivery_city = models.ForeignKey(DeliveryCity, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2) # Grand total including delivery
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False) # Simple paid status
    # You might want to add more fields like postal_code, status (e.g., pending, shipped, delivered)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id} by {self.first_name} {self.last_name}"

    def get_subtotal(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    variation = models.ForeignKey('ProductVariation', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        if self.variation:
            return f"{self.quantity} x {self.product.name} ({self.variation.color_name}) for Order {self.order.id}"
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"

    def get_cost(self):
        if self.price is not None and self.quantity is not None:
            return self.price * self.quantity
        return Decimal('0.00')

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50, help_text="e.g., Red, Blue, Green")
    image = models.ImageField(upload_to='products/variations/', null=True, blank=True, help_text="Image specific to this color variation.")
    # Add other variation-specific fields if needed, e.g.:
    # sku_suffix = models.CharField(max_length=50, blank=True, null=True)
    # stock = models.PositiveIntegerField(default=0)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price difference for this variation, if any.")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('product', 'color_name') # Ensure a product can't have the same color name twice
        verbose_name = "Product Variation"
        verbose_name_plural = "Product Variations"
        ordering = ['product', 'color_name']

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', help_text="Additional image for the product gallery.")
    alt_text = models.CharField(max_length=255, blank=True, null=True, help_text="Descriptive text for the image.")
    order = models.PositiveIntegerField(default=0, help_text="Display order of the image in the gallery.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ['product', 'order']

    def __str__(self):
        return f"Image for {self.product.name} (Order: {self.order})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Fields for checkout pre-fill
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    # address_line_2 = models.CharField(max_length=255, blank=True, null=True) # Optional
    city = models.CharField(max_length=100, blank=True, null=True)
    # postal_code = models.CharField(max_length=20, blank=True, null=True) # Removed
    # country = models.CharField(max_length=100, blank=True, null=True) # Optional

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Ensure profile exists, create if not (e.g., for existing users without profiles)
        UserProfile.objects.get_or_create(user=instance)
        # instance.profile.save() # Use this if you have fields on UserProfile that need updating based on User model changes.
                                # For now, get_or_create is sufficient.
