from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Category

class ProductFilterForm(forms.Form):
    min_price = forms.DecimalField(label='Min Price', required=False, min_value=0)
    max_price = forms.DecimalField(label='Max Price', required=False, min_value=0)
    
    # Category filter - will be populated dynamically in the view
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Will be set in __init__
        label='Category',
        required=False,
        empty_label="All Categories"
    )
    
    # Color filter based on ProductVariation
    color = forms.ChoiceField(
        label='Color',
        required=False,
        choices=[('', 'All Colors')],  # Will be populated in __init__
    )
    
    # Size filter (assuming sizes might be added in the future)
    SIZE_CHOICES = [
        ('', 'All Sizes'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    size = forms.ChoiceField(
        label='Size',
        required=False,
        choices=SIZE_CHOICES,
    )
    
    # Brand filter (assuming brands might be added in the future)
    brand = forms.ChoiceField(
        label='Brand',
        required=False,
        choices=[('', 'All Brands')],  # Will be populated in __init__
    )
    
    # Rating filter
    RATING_CHOICES = [
        ('', 'All Ratings'),
        ('5', '5 Stars'),
        ('4', '4+ Stars'),
        ('3', '3+ Stars'),
        ('2', '2+ Stars'),
        ('1', '1+ Star'),
    ]
    rating = forms.ChoiceField(
        label='Rating',
        required=False,
        choices=RATING_CHOICES,
    )
    
    order_by = forms.ChoiceField(
        label='Sort By',
        required=False,
        choices=[
            ('', '---------'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('name', 'Name: A to Z'),
            ('-name', 'Name: Z to A'),
        ]
    )
    
    def __init__(self, *args, **kwargs):
        category_queryset = kwargs.pop('category_queryset', None)
        color_choices = kwargs.pop('color_choices', None)
        brand_choices = kwargs.pop('brand_choices', None)
        
        super().__init__(*args, **kwargs)
        
        # Set category queryset if provided
        if category_queryset is not None:
            self.fields['category'].queryset = category_queryset
            
        # Set color choices if provided
        if color_choices is not None:
            self.fields['color'].choices = [('', 'All Colors')] + color_choices
            
        # Set brand choices if provided
        if brand_choices is not None:
            self.fields['brand'].choices = [('', 'All Brands')] + brand_choices


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address_line_1', 'city']
        # You can add widgets or labels here if needed, e.g.:
        # labels = {
        #     'address_line_1': 'Address',
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate first_name and last_name from the User instance if available
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        # Save UserProfile part
        profile = super().save(commit=False)
        
        # Save User part
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        
        if commit:
            user.save()
            profile.save()
        return profile
