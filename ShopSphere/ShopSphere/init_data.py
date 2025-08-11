from app import db
from models import Category, Product, Inventory, User, Discount
from datetime import datetime, timedelta

def init_sample_data():
    """Initialize sample data if not exists"""
    
    # Create categories if they don't exist
    categories_data = [
        {'name': 'Shirts', 'description': 'Stylish shirts for all occasions'},
        {'name': 'Trousers', 'description': 'Comfortable and fashionable trousers'},
        {'name': 'Footwear', 'description': 'Trendy shoes and footwear'},
        {'name': 'Combos', 'description': 'Complete outfit combinations'}
    ]
    
    for cat_data in categories_data:
        if not Category.query.filter_by(name=cat_data['name']).first():
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()
    
    # Get categories
    shirts_cat = Category.query.filter_by(name='Shirts').first()
    trousers_cat = Category.query.filter_by(name='Trousers').first()
    footwear_cat = Category.query.filter_by(name='Footwear').first()
    combos_cat = Category.query.filter_by(name='Combos').first()
    
    # Create products based on attached file names
    products_data = [
        # Shirts
        {
            'name': 'Black And White Striped Corset Fitted Shirt',
            'description': 'Stylish black and white striped corset fitted shirt perfect for formal and casual occasions.',
            'price': 799,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/black_white_striped_corset_shirt.jpg'
        },
        {
            'name': 'Black Shirt with Pleated Peplum Waist and Button Closure',
            'description': 'Elegant black shirt featuring pleated peplum waist and button closure for a sophisticated look.',
            'price': 799,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/black_pleated_peplum_shirt.jpg'
        },
        {
            'name': 'Collar Solid Button Long Sleeve White Shirt',
            'description': 'Classic white button-down shirt with collar and long sleeves, perfect for professional settings.',
            'price': 1048,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/white_collar_button_shirt.jpg'
        },
        {
            'name': 'Collar Striped Long Sleeve Shirt',
            'description': 'Trendy striped long sleeve shirt with collar, great for casual and semi-formal occasions.',
            'price': 699,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/striped_long_sleeve_shirt.jpg'
        },
        {
            'name': 'Collar Striped Long Sleeve Shirt In Sage Green',
            'description': 'Beautiful sage green striped long sleeve shirt with collar, perfect for a fresh modern look.',
            'price': 649,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/sage_green_striped_shirt.jpg'
        },
        {
            'name': 'Square Neck Split Long Sleeve Top in Off-White',
            'description': 'Chic off-white top with square neck and split long sleeves for a contemporary style.',
            'price': 1048,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/off_white_square_neck_top.jpg'
        },
        {
            'name': 'V Neck Wrap Front With Lantern Sleeve Top in Off-White',
            'description': 'Elegant off-white wrap front top with v-neck and lantern sleeves for a romantic look.',
            'price': 499,
            'category_id': shirts_cat.id,
            'image_url': '/static/images/off_white_wrap_lantern_top.jpg'
        },
        
        # Trousers
        {
            'name': 'High Waist Pleated Trousers In Black',
            'description': 'Sophisticated high waist pleated trousers in classic black, perfect for office wear.',
            'price': 999,
            'category_id': trousers_cat.id,
            'image_url': '/static/images/black_pleated_trousers.jpg'
        },
        {
            'name': 'High Waist Pleated Trousers In White',
            'description': 'Elegant high waist pleated trousers in crisp white, ideal for formal occasions.',
            'price': 899,
            'category_id': trousers_cat.id,
            'image_url': '/static/images/white_pleated_trousers.jpg'
        },
        {
            'name': 'Light Brown Premium Trousers',
            'description': 'Premium quality light brown trousers with excellent fit and comfort.',
            'price': 699,
            'category_id': trousers_cat.id,
            'image_url': '/static/images/light_brown_premium_trousers.jpg'
        },
        
        # Footwear
        {
            'name': 'Black Kitten Heels Pumps',
            'description': 'Classic black kitten heel pumps, comfortable and stylish for everyday wear.',
            'price': 1019,
            'category_id': footwear_cat.id,
            'image_url': '/static/images/black_kitten_heels.jpg'
        },
        {
            'name': 'Kitten Pump Shoes',
            'description': 'Elegant kitten pump shoes perfect for professional and formal occasions.',
            'price': 1499,
            'category_id': footwear_cat.id,
            'image_url': '/static/images/kitten_pump_shoes.jpg'
        },
        {
            'name': 'Square Toe Ballerina Burgundy Flats Shoes',
            'description': 'Comfortable burgundy ballerina flats with square toe design for casual wear.',
            'price': 999,
            'category_id': footwear_cat.id,
            'image_url': '/static/images/burgundy_ballerina_flats.jpg'
        },
        
        # Combos
        {
            'name': 'V-neck Solid Button Vest & Mid Rise Pocket Wide Leg Trousers In Black',
            'description': 'Complete black outfit with v-neck button vest and wide leg trousers with pockets.',
            'price': 1349,
            'category_id': combos_cat.id,
            'image_url': '/static/images/black_vest_trousers_combo.jpg'
        },
        {
            'name': 'V-Neck Solid Button Vest & Mid Rise Pocket Wide Leg Trousers In Burgundy',
            'description': 'Elegant burgundy outfit combination with v-neck vest and wide leg trousers.',
            'price': 1499,
            'category_id': combos_cat.id,
            'image_url': '/static/images/burgundy_vest_trousers_combo.jpg'
        }
    ]
    
    # Add products if they don't exist
    for prod_data in products_data:
        if not Product.query.filter_by(name=prod_data['name']).first():
            product = Product(**prod_data)
            db.session.add(product)
            db.session.flush()  # Get product ID
            
            # Add inventory for each size
            sizes = ['XS', 'S', 'M', 'L', 'XL']
            for size in sizes:
                inventory = Inventory(
                    product_id=product.id,
                    size=size,
                    quantity=20  # Initial stock
                )
                db.session.add(inventory)
    
    # Create super admin if not exists
    if not User.query.filter_by(email='sharaanncharles@gmail.com').first():
        admin = User(
            username='sharaanncharles',
            email='sharaanncharles@gmail.com',
            full_name='Shara Ann Charles',
            phone='9999999999',
            is_admin=True,
            admin_level='super_admin',
            is_verified=True
        )
        admin.set_password('EMma@123')
        db.session.add(admin)
    
    # Create sample discounts
    discounts_data = [
        {
            'code': 'WELCOME10',
            'description': 'Welcome discount for new customers',
            'discount_type': 'percentage',
            'discount_value': 10,
            'min_order_amount': 500,
            'max_discount': 200,
            'usage_limit': 100,
            'valid_until': datetime.utcnow() + timedelta(days=30)
        },
        {
            'code': 'FLAT200',
            'description': 'Flat 200 off on orders above 1000',
            'discount_type': 'fixed',
            'discount_value': 200,
            'min_order_amount': 1000,
            'usage_limit': 50,
            'valid_until': datetime.utcnow() + timedelta(days=15)
        }
    ]
    
    for disc_data in discounts_data:
        if not Discount.query.filter_by(code=disc_data['code']).first():
            discount = Discount(**disc_data)
            db.session.add(discount)
    
    db.session.commit()
    # Create admin user
    if not User.query.filter_by(email='sharaanncharles@gmail.com').first():
        admin_user = User()
        admin_user.username = 'sharaanncharles@gmail.com'
        admin_user.email = 'sharaanncharles@gmail.com'
        admin_user.full_name = 'Sharaan Charles'
        admin_user.phone = '+91-9876543210'
        admin_user.is_admin = True
        admin_user.admin_level = 'super_admin'
        admin_user.is_verified = True
        admin_user.loyalty_points = 1000
        admin_user.membership_tier = 'platinum'
        admin_user.set_password('EMma@123')
        db.session.add(admin_user)
        db.session.commit()
    
    print("Sample data initialized successfully!")
