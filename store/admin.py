from django import forms # Import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Product, SliderImage, MobileSliderImage, Category, LogoCarouselItem, DeliveryCity, Order, OrderItem, ProductVariation, ProductImage, UserProfile

class CategoryAdmin(admin.ModelAdmin): # New admin class for Category
    list_display = ('name', 'parent', 'slug', 'image_thumbnail', 'product_count')
    search_fields = ('name', 'description', 'parent__name')
    list_filter = ('parent',) # Allow filtering by parent
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'parent', 'image', 'description') # Add image to fields

    def image_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'Image'

    def product_count(self, obj): # Method to display product count
        return obj.products.count()
    product_count.short_description = 'No. of Products'

# Define Inlines first
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'order')
    ordering = ('order',)

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ('color_name', 'image', 'is_active')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    list_editable = ('price', 'is_active')
    search_fields = ('name', 'short_description', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    inlines = [ProductImageInline, ProductVariationInline] # Now these are defined

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'short_description':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 10, 'cols': 70})
        elif db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 10, 'cols': 70})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'uploaded_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'caption')
    ordering = ('order',)

class MobileSliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'uploaded_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'caption')
    ordering = ('order',)
    # verbose_name = "Mobile Slider Image" # This is set in Model's Meta, not needed here unless overriding

class LogoCarouselItemAdmin(admin.ModelAdmin): # New admin class
    list_display = ('name', 'order', 'is_active', 'link_url', 'uploaded_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active', 'link_url')
    search_fields = ('name',)
    ordering = ('order', 'name')

class DeliveryCityAdmin(admin.ModelAdmin):
    list_display = ('name', 'delivery_fee', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('delivery_fee', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variation'] # Add variation to raw_id_fields
    fields = ('product', 'variation', 'quantity', 'price', 'get_cost_display') # Explicitly order fields
    readonly_fields = ('product', 'variation', 'price', 'get_cost_display') # Make product and variation read-only too
    extra = 0

    # get_cost_display can still be used for list_display in OrderItemAdmin if registered separately,
    # but it's not suitable for readonly_fields in the inline "add" form.
    # For displaying in the inline for existing items, we might need a different approach
    # or accept it won't show until saved. Or, add it as a non-editable display field if possible.
    # For now, removing it from readonly_fields is the simplest fix for the add form error.

    def get_cost_display(self, obj):
        return f"{obj.get_cost()} DH"
    get_cost_display.short_description = 'Item Total'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'city_name', 'total_amount', 'paid', 'created_at')
    list_filter = ('paid', 'created_at', 'updated_at', 'delivery_city')
    search_fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'city_name')
    inlines = [OrderItemInline]
    
    # Consolidated readonly_fields for the detail/edit view
    readonly_fields_on_edit = ('id', 'created_at', 'updated_at', 'get_subtotal_display', 'delivery_fee', 'total_amount')

    fieldsets = (
        ('Order Information', {
            'fields': ('id', ('first_name', 'last_name'), ('email', 'phone_number'), 'paid')
        }),
        ('Shipping Details', {
            'fields': ('address', 'city_name', 'delivery_city', 'delivery_fee') # 'delivery_fee' is also here
        }),
        ('Totals & Timestamps', {
            'fields': ('get_subtotal_display', 'total_amount', 'created_at', 'updated_at') # Removed duplicate 'delivery_fee'
        }),
    )
    # Apply the consolidated readonly_fields for the edit/detail view
    # 'get_subtotal_display' is already in readonly_fields_on_edit
    readonly_fields = readonly_fields_on_edit


    def get_subtotal_display(self, obj):
        return f"{obj.get_subtotal()} DH"
    get_subtotal_display.short_description = 'Subtotal (Calculated)'


admin.site.register(Category, CategoryAdmin) # Register Category
admin.site.register(Product, ProductAdmin)
admin.site.register(SliderImage, SliderImageAdmin)
admin.site.register(MobileSliderImage, MobileSliderImageAdmin)
admin.site.register(LogoCarouselItem, LogoCarouselItemAdmin)
admin.site.register(DeliveryCity, DeliveryCityAdmin)
admin.site.register(Order, OrderAdmin)
# ProductImage is managed via ProductAdmin inline
# ProductVariation is managed via ProductAdmin inline
# OrderItem is managed via OrderAdmin inline

# UserProfile Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    # fields = ('phone_number', 'address') # Add fields you want to edit here

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_profile_info') # Add custom display

    def get_profile_info(self, instance):
        # Example: return instance.profile.phone_number
        return "View/Edit Profile Inline" # Placeholder
    get_profile_info.short_description = 'Profile Info'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Optionally, register UserProfile directly if you want a separate admin page for it
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'created_at', 'updated_at') # Add fields you want to see
#     search_fields = ('user__username', 'user__email')
# admin.site.register(UserProfile, UserProfileAdmin)
