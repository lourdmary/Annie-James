import os
import random
import string
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import (User, Product, Category, Inventory, Order, OrderItem, 
                   CartItem, WishlistItem, Comment, Like, Discount, OTPVerification)
from utils import send_otp_email, calculate_loyalty_points, calculate_discount, validate_password, create_razorpay_order, verify_razorpay_payment

@app.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', products=featured_products, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        
        # Validate password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            flash(message, 'danger')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Use email as username
        username = data['email']
        
        # Generate and send OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Save user data in session temporarily
        session['registration_data'] = {
            'username': username,
            'email': data['email'],
            'password': data['password'],
            'full_name': data['full_name'],
            'phone': data['phone']
        }
        
        # Save OTP to database
        otp_record = OTPVerification()
        otp_record.email = data['email']
        otp_record.otp = otp
        otp_record.purpose = 'registration'
        db.session.add(otp_record)
        db.session.commit()
        
        # Send OTP email
        if send_otp_email(data['email'], otp):
            flash('OTP sent to your email. Please verify to complete registration.', 'info')
            return redirect(url_for('verify_otp', purpose='registration'))
        else:
            flash('Failed to send OTP. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/verify_otp/<purpose>', methods=['GET', 'POST'])
def verify_otp(purpose):
    if request.method == 'POST':
        otp = request.form['otp']
        
        if purpose == 'registration':
            email = session.get('registration_data', {}).get('email')
            if not email:
                flash('Session expired. Please register again.', 'danger')
                return redirect(url_for('register'))
            
            # Verify OTP
            otp_record = OTPVerification.query.filter_by(
                email=email, otp=otp, purpose='registration', is_used=False
            ).first()
            
            if otp_record and otp_record.created_at > datetime.utcnow() - timedelta(minutes=10):
                # Create user
                data = session['registration_data']
                user = User()
                user.username = data['username']
                user.email = data['email']
                user.full_name = data['full_name']
                user.phone = data['phone']
                user.is_verified = True
                user.set_password(data['password'])
                
                db.session.add(user)
                otp_record.is_used = True
                db.session.commit()
                
                # Clear session data
                session.pop('registration_data', None)
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid or expired OTP', 'danger')
        
        elif purpose == 'password_reset':
            email = session.get('reset_email')
            if not email:
                flash('Session expired. Please try again.', 'danger')
                return redirect(url_for('forgot_password'))
            
            otp_record = OTPVerification.query.filter_by(
                email=email, otp=otp, purpose='password_reset', is_used=False
            ).first()
            
            if otp_record and otp_record.created_at > datetime.utcnow() - timedelta(minutes=10):
                otp_record.is_used = True
                db.session.commit()
                return redirect(url_for('reset_password'))
            else:
                flash('Invalid or expired OTP', 'danger')
    
    return render_template('verify_otp.html', purpose=purpose)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check both email and username for login compatibility
        user = User.query.filter((User.email == username) | (User.username == username)).first()
        
        if user and user.check_password(password):
            if user.is_verified:
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Please verify your email before logging in', 'warning')
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate and send OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            otp_record = OTPVerification()
            otp_record.email = email
            otp_record.otp = otp
            otp_record.purpose = 'password_reset'
            db.session.add(otp_record)
            db.session.commit()
            
            session['reset_email'] = email
            
            if send_otp_email(email, otp):
                flash('OTP sent to your email', 'info')
                return redirect(url_for('verify_otp', purpose='password_reset'))
            else:
                flash('Failed to send OTP. Please try again.', 'danger')
        else:
            flash('Email not found', 'danger')
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash('Session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.set_password(password)
            db.session.commit()
            session.pop('reset_email', None)
            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

@app.route('/products')
def products():
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, 
                         selected_category=category_id, search=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    comments = Comment.query.filter_by(product_id=product_id).order_by(Comment.created_at.desc()).all()
    sizes = [inv.size for inv in product.inventory if inv.quantity > 0]
    
    # Check if user has liked this product
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
    
    return render_template('product_detail.html', product=product, comments=comments, 
                         sizes=sizes, user_liked=user_liked)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    size = request.form.get('size')
    quantity = request.form.get('quantity', 1, type=int)
    
    # Check if item already in cart
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product_id, size=size
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem()
        cart_item.user_id = current_user.id
        cart_item.product_id = product_id
        cart_item.size = size
        cart_item.quantity = quantity
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Item added to cart', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.get_price() * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart', 'info')
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    for key, value in request.form.items():
        if key.startswith('quantity_'):
            item_id = int(key.replace('quantity_', ''))
            quantity = int(value)
            
            item = CartItem.query.get(item_id)
            if item and item.user_id == current_user.id:
                if quantity > 0:
                    item.quantity = quantity
                else:
                    db.session.delete(item)
    
    db.session.commit()
    flash('Cart updated', 'success')
    return redirect(url_for('cart'))

@app.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    existing_item = WishlistItem.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()
    
    if not existing_item:
        wishlist_item = WishlistItem()
        wishlist_item.user_id = current_user.id
        wishlist_item.product_id = product_id
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Item added to wishlist', 'success')
    else:
        flash('Item already in wishlist', 'info')
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/remove_from_wishlist/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from wishlist', 'info')
    return redirect(url_for('wishlist'))

@app.route('/like_product/<int:product_id>')
@login_required
def like_product(product_id):
    existing_like = Like.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = Like()
        like.user_id = current_user.id
        like.product_id = product_id
        db.session.add(like)
        liked = True
    
    db.session.commit()
    
    product = Product.query.get(product_id)
    likes_count = product.get_likes_count()
    
    return jsonify({'liked': liked, 'likes_count': likes_count})

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    product_id = request.form.get('product_id', type=int)
    content = request.form.get('content')
    rating = request.form.get('rating', type=int)
    
    comment = Comment()
    comment.user_id = current_user.id
    comment.product_id = product_id
    comment.content = content
    comment.rating = rating
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    subtotal = sum(item.product.get_price() * item.quantity for item in cart_items)
    
    # Check available discounts
    available_discounts = Discount.query.filter(
        Discount.is_active == True,
        Discount.min_order_amount <= subtotal,
        Discount.valid_until > datetime.utcnow()
    ).all()
    
    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal,
                         available_discounts=available_discounts)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    # Get form data
    payment_method = request.form.get('payment_method')
    house_number = request.form.get('house_number')
    street_name = request.form.get('street_name')
    address_line = request.form.get('address_line')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')
    discount_code = request.form.get('discount_code')
    use_loyalty_points = request.form.get('use_loyalty_points', type=int, default=0)
    
    # Validate COD for specific cities
    if payment_method == 'COD' and city not in ['Bangalore', 'Mumbai', 'Chennai']:
        flash('COD is only available in Bangalore, Mumbai, and Chennai', 'danger')
        return redirect(url_for('checkout'))
    
    # Calculate total
    subtotal = sum(item.product.get_price() * item.quantity for item in cart_items)
    discount_amount = 0
    
    # Apply discount
    if discount_code:
        discount_amount = calculate_discount(discount_code, subtotal)
    
    # Apply loyalty points
    loyalty_discount = min(use_loyalty_points, current_user.loyalty_points, subtotal * 0.1)
    
    total_amount = subtotal - discount_amount - loyalty_discount
    
    # Handle Razorpay payment
    if payment_method == 'Razorpay':
        success, razorpay_order = create_razorpay_order(total_amount)
        if not success:
            flash('Payment processing failed. Please try again.', 'danger')
            return redirect(url_for('checkout'))
        
        # Store order data in session for payment completion
        session['pending_order'] = {
            'cart_items': [{'product_id': item.product_id, 'quantity': item.quantity, 'size': item.size, 'price': item.product.get_price()} for item in cart_items],
            'total_amount': total_amount,
            'discount_amount': discount_amount,
            'loyalty_points_used': use_loyalty_points,
            'address': {
                'house_number': house_number,
                'street_name': street_name,
                'address_line': address_line,
                'city': city,
                'state': state,
                'pincode': pincode
            },
            'razorpay_order_id': razorpay_order['id']
        }
        
        return render_template('payment.html', 
                             order=razorpay_order, 
                             total_amount=total_amount,
                             razorpay_key_id=os.environ.get('RAZORPAY_KEY_ID'))
    
    # Create order
    order = Order()
    order.user_id = current_user.id
    order.total_amount = total_amount
    order.discount_amount = discount_amount
    order.loyalty_points_used = use_loyalty_points
    order.payment_method = payment_method
    order.shipping_house_number = house_number
    order.shipping_street_name = street_name
    order.shipping_address_line = address_line
    order.shipping_city = city
    order.shipping_state = state
    order.shipping_pincode = pincode
    order.payment_status = 'completed' if payment_method == 'COD' else 'pending'
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Create order items
    for item in cart_items:
        order_item = OrderItem()
        order_item.order_id = order.id
        order_item.product_id = item.product_id
        order_item.quantity = item.quantity
        order_item.size = item.size
        order_item.price = item.product.get_price()
        db.session.add(order_item)
        
        # Update inventory
        inventory = Inventory.query.filter_by(
            product_id=item.product_id, size=item.size
        ).first()
        if inventory:
            inventory.quantity -= item.quantity
    
    # Update user loyalty points
    current_user.loyalty_points -= use_loyalty_points
    current_user.loyalty_points += calculate_loyalty_points(total_amount)
    
    # Clear cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_success', order_id=order.id))

@app.route('/order_success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Dashboard statistics
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    total_customers = User.query.filter_by(is_admin=False).count()
    pending_orders = Order.query.filter_by(order_status='placed').count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_orders=total_orders, total_revenue=total_revenue,
                         total_customers=total_customers, pending_orders=pending_orders,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/size_chart')
def size_chart():
    return render_template('size_chart.html')

@app.route('/payment_success', methods=['POST'])
@login_required
def payment_success():
    """Handle successful Razorpay payment"""
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    signature = request.form.get('razorpay_signature')
    
    # Verify payment
    if not verify_razorpay_payment(payment_id, order_id, signature):
        flash('Payment verification failed', 'danger')
        return redirect(url_for('checkout'))
    
    # Get pending order from session
    pending_order = session.get('pending_order')
    if not pending_order or pending_order.get('razorpay_order_id') != order_id:
        flash('Order session expired', 'danger')
        return redirect(url_for('cart'))
    
    # Create order
    order = Order()
    order.user_id = current_user.id
    order.total_amount = pending_order['total_amount']
    order.discount_amount = pending_order['discount_amount']
    order.loyalty_points_used = pending_order['loyalty_points_used']
    order.payment_method = 'Razorpay'
    order.payment_id = payment_id
    order.payment_status = 'completed'
    
    # Set address
    address = pending_order['address']
    order.shipping_house_number = address['house_number']
    order.shipping_street_name = address['street_name']
    order.shipping_address_line = address['address_line']
    order.shipping_city = address['city']
    order.shipping_state = address['state']
    order.shipping_pincode = address['pincode']
    
    db.session.add(order)
    db.session.flush()
    
    # Create order items
    for item_data in pending_order['cart_items']:
        order_item = OrderItem()
        order_item.order_id = order.id
        order_item.product_id = item_data['product_id']
        order_item.quantity = item_data['quantity']
        order_item.size = item_data['size']
        order_item.price = item_data['price']
        db.session.add(order_item)
        
        # Update inventory
        inventory = Inventory.query.filter_by(
            product_id=item_data['product_id'], size=item_data['size']
        ).first()
        if inventory:
            inventory.quantity -= item_data['quantity']
    
    # Update user loyalty points
    current_user.loyalty_points -= pending_order['loyalty_points_used']
    current_user.loyalty_points += calculate_loyalty_points(pending_order['total_amount'])
    
    # Clear cart and session
    CartItem.query.filter_by(user_id=current_user.id).delete()
    session.pop('pending_order', None)
    
    db.session.commit()
    
    flash('Payment successful! Order placed.', 'success')
    return redirect(url_for('order_success', order_id=order.id))

@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    customers = User.query.filter_by(is_admin=False).all()
    return render_template('admin/customers.html', customers=customers)

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    # Sales analytics
    daily_sales = db.session.query(
        db.func.date(Order.created_at).label('date'),
        db.func.sum(Order.total_amount).label('total')
    ).group_by(db.func.date(Order.created_at)).all()
    
    # Category wise sales
    category_sales = db.session.query(
        Category.name,
        db.func.sum(OrderItem.price * OrderItem.quantity).label('total')
    ).join(Product).join(OrderItem).group_by(Category.id).all()
    
    return render_template('admin/analytics.html', daily_sales=daily_sales, 
                         category_sales=category_sales)

@app.route('/admin/team')
@login_required
def admin_team():
    if not current_user.is_super_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    team_members = User.query.filter(User.admin_level.in_(['super_admin', 'limited_admin'])).all()
    return render_template('admin/team.html', team_members=team_members)

@app.route('/admin/discounts')
@login_required
def admin_discounts():
    if not current_user.can_access_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    discounts = Discount.query.order_by(Discount.created_at.desc()).all()
    return render_template('admin/discounts.html', discounts=discounts)

@app.route('/admin/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    if not current_user.can_access_admin():
        return jsonify({'success': False, 'message': 'Access denied'})
    
    order_id = request.form.get('order_id', type=int)
    new_status = request.form.get('status')
    
    order = Order.query.get(order_id)
    if order:
        order.order_status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Order not found'})
