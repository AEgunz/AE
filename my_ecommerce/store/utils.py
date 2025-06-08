from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_notification(phone_number, message):
    """
    Send a WhatsApp notification to the specified phone number.
    
    This is a placeholder function that logs the message that would be sent.
    In a production environment, this would be implemented with a WhatsApp API
    service like Twilio, MessageBird, or WhatsApp Business API.
    
    Args:
        phone_number: The phone number to send the notification to
        message: The message to send
    """
    if not phone_number:
        logger.warning("No phone number provided for WhatsApp notification")
        return
    
    # Log the message that would be sent
    logger.info(f"WhatsApp notification would be sent to {phone_number}: {message}")
    
    # In production, you would implement the actual WhatsApp API call here
    # Example with Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=message,
    #     from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
    #     to=f"whatsapp:{phone_number}"
    # )
    
    # For now, just print to console for development
    print(f"\n----- WHATSAPP NOTIFICATION -----")
    print(f"To: {phone_number}")
    print(f"Message: {message}")
    print(f"---------------------------------\n")


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
    
    # Send WhatsApp notification if phone number is available
    if hasattr(settings, 'ADMIN_WHATSAPP') and settings.ADMIN_WHATSAPP:
        # Create a simple text message for WhatsApp
        whatsapp_message = f"""
New Order #{order.id} Received!

Customer: {order.first_name} {order.last_name}
Phone: {order.phone_number}
Total Amount: {order.total_amount} MAD
Items: {order.items.count()}

Log in to the admin panel to view details.
"""
        send_whatsapp_notification(settings.ADMIN_WHATSAPP, whatsapp_message)
