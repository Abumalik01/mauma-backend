from flask import Blueprint, jsonify
from src.models.user import db, User
from src.models.product import Product, Category

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed-data', methods=['POST'])
def seed_data():
    """Seed the database with initial data"""
    try:
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Smartphones, tablets, and gadgets', 'icon': 'smartphone'},
            {'name': 'Fashion', 'description': 'Clothing, shoes, and accessories', 'icon': 'shirt'},
            {'name': 'Home Appliances', 'description': 'Kitchen and household items', 'icon': 'home'},
            {'name': 'Building Materials', 'description': 'Construction and tools', 'icon': 'wrench'},
            {'name': 'Automotive', 'description': 'Vehicles and automotive parts', 'icon': 'car'}
        ]
        
        categories = {}
        for cat_data in categories_data:
            existing_cat = Category.query.filter_by(name=cat_data['name']).first()
            if not existing_cat:
                category = Category(**cat_data)
                db.session.add(category)
                db.session.flush()
                categories[cat_data['name']] = category.id
            else:
                categories[cat_data['name']] = existing_cat.id
        
        # Create sample products
        products_data = [
            {
                'name': 'Xiaomi Redmi Note 12 Pro 5G Smartphone',
                'description': 'Latest 5G smartphone with advanced camera system and long-lasting battery',
                'price': 120000,
                'original_price': 150000,
                'category': 'Electronics',
                'brand': 'Xiaomi',
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
                'stock_quantity': 50,
                'rating': 4.2,
                'review_count': 156,
                'is_featured': True
            },
            {
                'name': 'Apple Watch Series 8 Smart Watch',
                'description': 'Advanced health monitoring and fitness tracking smartwatch',
                'price': 85000,
                'category': 'Electronics',
                'brand': 'Apple',
                'image_url': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&h=400&fit=crop',
                'stock_quantity': 30,
                'rating': 4.8,
                'review_count': 89,
                'is_featured': True
            },
            {
                'name': 'Sony WH-1000XM4 Wireless Headphones',
                'description': 'Industry-leading noise canceling wireless headphones',
                'price': 45000,
                'original_price': 55000,
                'category': 'Electronics',
                'brand': 'Sony',
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
                'stock_quantity': 75,
                'rating': 4.6,
                'review_count': 234,
                'is_featured': True
            },
            {
                'name': 'Samsung 55" 4K Smart TV',
                'description': 'Ultra HD 4K Smart TV with HDR and built-in streaming apps',
                'price': 280000,
                'category': 'Electronics',
                'brand': 'Samsung',
                'image_url': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop',
                'stock_quantity': 20,
                'rating': 4.4,
                'review_count': 67,
                'is_featured': True
            },
            {
                'name': 'Nike Air Max 270 Running Shoes',
                'description': 'Comfortable running shoes with Air Max cushioning technology',
                'price': 25000,
                'original_price': 32000,
                'category': 'Fashion',
                'brand': 'Nike',
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
                'stock_quantity': 100,
                'rating': 4.3,
                'review_count': 145,
                'is_featured': True
            },
            {
                'name': 'Instant Pot Duo 7-in-1 Electric Pressure Cooker',
                'description': 'Multi-functional electric pressure cooker for quick and easy cooking',
                'price': 35000,
                'category': 'Home Appliances',
                'brand': 'Instant Pot',
                'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop',
                'stock_quantity': 60,
                'rating': 4.7,
                'review_count': 98,
                'is_featured': True
            },
            {
                'name': 'Adidas Ultraboost 22 Running Shoes',
                'description': 'Premium running shoes with responsive Boost midsole',
                'price': 28000,
                'original_price': 35000,
                'category': 'Fashion',
                'brand': 'Adidas',
                'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop',
                'stock_quantity': 80,
                'rating': 4.5,
                'review_count': 112,
                'is_featured': True
            },
            {
                'name': 'Dyson V15 Detect Cordless Vacuum',
                'description': 'Powerful cordless vacuum with laser dust detection',
                'price': 95000,
                'category': 'Home Appliances',
                'brand': 'Dyson',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',
                'stock_quantity': 25,
                'rating': 4.9,
                'review_count': 76,
                'is_featured': True
            },
            {
                'name': 'iPhone 14 Pro Max',
                'description': 'Latest iPhone with Pro camera system and A16 Bionic chip',
                'price': 450000,
                'original_price': 500000,
                'category': 'Electronics',
                'brand': 'Apple',
                'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',
                'stock_quantity': 15,
                'rating': 4.8,
                'review_count': 203,
                'is_featured': True
            },
            {
                'name': 'Levi\'s 501 Original Jeans',
                'description': 'Classic straight-leg jeans made from premium denim',
                'price': 15000,
                'original_price': 18000,
                'category': 'Fashion',
                'brand': 'Levi\'s',
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop',
                'stock_quantity': 120,
                'rating': 4.1,
                'review_count': 89,
                'is_featured': False
            }
        ]
        
        # Create a default user if not exists
        default_user = User.query.filter_by(email='demo@mauma.ng').first()
        if not default_user:
            user = User(
                username='demo_user',
                email='demo@mauma.ng'
            )
            db.session.add(user)
        
        # Add products
        for product_data in products_data:
            existing_product = Product.query.filter_by(name=product_data['name']).first()
            if not existing_product:
                category_name = product_data.pop('category')
                product_data['category_id'] = categories[category_name]
                
                product = Product(**product_data)
                db.session.add(product)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database seeded successfully with sample data'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

