import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'simple_app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app, origins=['*'])

# Initialize database
db = SQLAlchemy(app)

# Simple models without complex relationships
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    category_id = db.Column(db.Integer)
    brand = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        discount = None
        if self.original_price and self.original_price > self.price:
            discount = round(((self.original_price - self.price) / self.original_price * 100), 0)
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'original_price': self.original_price,
            'category_id': self.category_id,
            'brand': self.brand,
            'image_url': self.image_url,
            'rating': self.rating,
            'review_count': self.review_count,
            'is_featured': self.is_featured,
            'discount_percentage': discount
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'MAUMA API is running'})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({
            'success': True,
            'categories': [cat.to_dict() for cat in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        featured = request.args.get('featured', type=bool)
        category_id = request.args.get('category_id', type=int)
        
        query = Product.query
        
        if featured is not None:
            query = query.filter(Product.is_featured == featured)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        products = query.all()
        
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/seed-data', methods=['POST'])
def seed_data():
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
                'rating': 4.9,
                'review_count': 76,
                'is_featured': True
            }
        ]
        
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

# Serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Frontend not built yet", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

