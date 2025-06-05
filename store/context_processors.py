from .cart import Cart
from .models import Category # Import Category model

def cart(request):
    return {'cart': Cart(request)}

def categories_processor(request):
    # Fetch all categories. The template will handle hierarchy.
    # Alternatively, fetch only top-level: Category.objects.filter(parent__isnull=True)
    # and then access children via category.children.all in the template.
    all_categories = Category.objects.all().order_by('name')
    return {'all_categories': all_categories}