from decimal import Decimal
from django.conf import settings
from .models import Product, ProductVariation

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def _generate_cart_item_id(self, product_id, variation_id=None):
        if variation_id:
            return f"{product_id}_{variation_id}"
        return str(product_id)

    def add(self, product, quantity=1, update_quantity=False, variation_id=None):
        """
        Add a product (and optionally a specific variation) to the cart or update its quantity.
        """
        product_id = str(product.id)
        actual_variation_id = str(variation_id) if variation_id else None
        cart_item_id = self._generate_cart_item_id(product_id, actual_variation_id)
        
        # Determine price - for now, use base product price.
        # Later, this could check variation.additional_price if that model field exists.
        item_price = product.price

        if cart_item_id not in self.cart:
            self.cart[cart_item_id] = {
                'product_id': product_id,
                'variation_id': actual_variation_id,
                'quantity': 0,
                'price': str(item_price)
            }

        if update_quantity:
            self.cart[cart_item_id]['quantity'] = quantity
        else:
            self.cart[cart_item_id]['quantity'] += quantity
        
        if self.cart[cart_item_id]['quantity'] <= 0: # Ensure quantity doesn't go below 0
             self.remove(product, variation_id=actual_variation_id)
        else:
            self.save()

    def update(self, product, quantity, variation_id=None):
        """
        Update the quantity of a product/variation in the cart.
        If quantity is 0 or less, remove the product/variation.
        """
        product_id = str(product.id)
        actual_variation_id = str(variation_id) if variation_id else None
        cart_item_id = self._generate_cart_item_id(product_id, actual_variation_id)
        quantity = int(quantity)

        if cart_item_id in self.cart:
            if quantity > 0:
                self.cart[cart_item_id]['quantity'] = quantity
                self.save()
            else:
                self.remove(product, variation_id=actual_variation_id)

    def save(self):
        self.session.modified = True

    def remove(self, product, variation_id=None):
        """
        Remove a product or a specific variation from the cart.
        """
        product_id = str(product.id)
        actual_variation_id = str(variation_id) if variation_id else None
        cart_item_id = self._generate_cart_item_id(product_id, actual_variation_id)

        if cart_item_id in self.cart:
            del self.cart[cart_item_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get products/variations from the database.
        """
        cart_item_ids = list(self.cart.keys()) # Use list for stable iteration if modifying
        
        # Prepare to fetch all products and variations in fewer queries
        product_ids_in_cart = set()
        variation_ids_in_cart = set()
        for item_id in cart_item_ids:
            item_data = self.cart.get(item_id)
            if item_data and 'product_id' in item_data: # Add check for product_id
                product_ids_in_cart.add(item_data['product_id'])
                if item_data.get('variation_id'):
                    variation_ids_in_cart.add(item_data['variation_id'])
            # else: item is malformed or old, consider logging or removing it
            # For now, it will be skipped by the next loop if product_id was missing

        products_db = {str(p.id): p for p in Product.objects.filter(id__in=list(product_ids_in_cart))}
        variations_db = {str(v.id): v for v in ProductVariation.objects.filter(id__in=list(variation_ids_in_cart))}

        cart_copy = self.cart.copy() # Iterate over a copy

        for item_id, item_data in cart_copy.items():
            # Ensure item_data has product_id before trying to access products_db
            if 'product_id' not in item_data:
                # This item is malformed or from an old session structure, skip it.
                # Optionally, you could try to remove it from self.cart here, but be cautious.
                continue

            product_instance = products_db.get(item_data['product_id'])
            if not product_instance:
                # Product might have been deleted from DB but still in cart session.
                # Consider removing from self.cart and saving.
                if item_id in self.cart: # Check if it's still in the live cart
                    del self.cart[item_id]
                    self.save()
                continue
            
            item_data['product'] = product_instance
            item_data['price'] = Decimal(item_data['price']) # Price stored at time of add
            item_data['total_price'] = item_data['price'] * item_data['quantity']
            item_data['cart_item_id'] = item_id # Pass the unique cart item ID
            
            if item_data.get('variation_id'):
                variation_id_for_lookup = str(item_data.get('variation_id')) # Ensure it's a string for dict lookup
                variation_instance = variations_db.get(variation_id_for_lookup)
                item_data['variation'] = variation_instance
                # If variation has its own image, prioritize it
                if variation_instance and variation_instance.image:
                    item_data['image_url'] = variation_instance.image.url
                elif product_instance.image:
                     item_data['image_url'] = product_instance.image.url
                else:
                    item_data['image_url'] = None # Or a placeholder
            elif product_instance.image:
                 item_data['image_url'] = product_instance.image.url
            else:
                item_data['image_url'] = None

            yield item_data


    def __len__(self):
        """
        Count all items in the cart (sum of quantities).
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()