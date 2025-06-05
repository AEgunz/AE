from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_notification_to_admin(order):
    """
    Send an email notification to admin users when a new order is placed.
    
    Args:
        order: The Order instance that was created
    """
    # Use the admin email from settings if available
    if hasattr(settings, 'ADMIN_EMAIL'):
        admin_emails = [settings.ADMIN_EMAIL]
    else:
        # Get all admin users
        admin_users = User.objects.filter(is_staff=True)
        admin_emails = [user.email for user in admin_users if user.email]
        
        # If no admin emails are found, use the first superuser's email
        if not admin_emails:
            superusers = User.objects.filter(is_superuser=True)
            admin_emails = [user.email for user in superusers if user.email]
        
        # If still no emails, return without sending
        if not admin_emails:
            return
    
    # Prepare email content
    subject = f'New Order #{order.id} Received'
    
    # Create HTML content
    html_message = render_to_string('store/email/order_notification.html', {
        'order': order,
        'order_items': order.items.all(),
    })
    
    # Create plain text content
    plain_message = strip_tags(html_message)
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        recipient_list=admin_emails,
        html_message=html_message,
        fail_silently=True,
    )
