import os
import requests
import logging
import razorpay
from datetime import datetime
from models import Discount

def send_otp_email(email, otp):
    """Send OTP email using Brevo API"""
    try:
        api_key = os.environ.get('BREVO_API_KEY', 'your-brevo-api-key-here')
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json'
        }
        
        data = {
            'sender': {'name': 'Annie James Zone', 'email': 'noreply@anniejaneszone.com'},
            'to': [{'email': email}],
            'subject': 'Your OTP for Annie James Zone',
            'htmlContent': f'''
            <html>
                <body>
                    <h2>Your OTP Code</h2>
                    <p>Your OTP code is: <strong>{otp}</strong></p>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            '''
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            logging.info(f"OTP email sent successfully to {email}")
            return True
        else:
            logging.error(f"Failed to send OTP email: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Error sending OTP email: {str(e)}")
        return False

def calculate_loyalty_points(order_amount):
    """Calculate loyalty points based on order amount"""
    # 1 point per 100 rupees spent
    return int(order_amount / 100)

def validate_password(password):
    """Validate password criteria: 8-20 chars, 1 lower, 1 upper, 1 special, 1 number"""
    import re
    
    if len(password) < 8 or len(password) > 20:
        return False, "Password must be between 8 and 20 characters"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Valid password"

def create_razorpay_order(amount, currency='INR'):
    """Create a Razorpay order"""
    try:
        client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET')))
        
        order_data = {
            'amount': int(amount * 100),  # Amount in paise
            'currency': currency,
            'payment_capture': 1
        }
        
        order = client.order.create(data=order_data)
        return True, order
        
    except Exception as e:
        logging.error(f"Failed to create Razorpay order: {str(e)}")
        return False, None

def verify_razorpay_payment(payment_id, order_id, signature):
    """Verify Razorpay payment"""
    try:
        client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_KEY_SECRET')))
        
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        return True
        
    except Exception as e:
        logging.error(f"Payment verification failed: {str(e)}")
        return False

def calculate_discount(discount_code, subtotal):
    """Calculate discount amount based on discount code"""
    discount = Discount.query.filter_by(code=discount_code, is_active=True).first()
    
    if not discount:
        return 0
    
    # Check if discount is valid
    if discount.valid_until and discount.valid_until < datetime.utcnow():
        return 0
    
    if discount.usage_limit and discount.used_count >= discount.usage_limit:
        return 0
    
    if subtotal < discount.min_order_amount:
        return 0
    
    # Calculate discount amount
    if discount.discount_type == 'percentage':
        discount_amount = (subtotal * discount.discount_value) / 100
        if discount.max_discount:
            discount_amount = min(discount_amount, discount.max_discount)
    else:  # fixed amount
        discount_amount = discount.discount_value
    
    # Update usage count
    discount.used_count += 1
    
    return discount_amount

def get_membership_benefits(tier):
    """Get membership benefits based on tier"""
    benefits = {
        'bronze': {
            'discount_percentage': 0,
            'free_shipping_threshold': 2000,
            'loyalty_multiplier': 1
        },
        'silver': {
            'discount_percentage': 5,
            'free_shipping_threshold': 1500,
            'loyalty_multiplier': 1.5
        },
        'gold': {
            'discount_percentage': 10,
            'free_shipping_threshold': 1000,
            'loyalty_multiplier': 2
        },
        'platinum': {
            'discount_percentage': 15,
            'free_shipping_threshold': 0,
            'loyalty_multiplier': 3
        }
    }
    return benefits.get(tier, benefits['bronze'])
