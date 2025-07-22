from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.product import Product, Category, Cart
from sqlalchemy import or_

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        featured = request.args.get('featured', type=bool)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        sort_by = request.args.get('sort_by', 'created_at')  # name, price, rating, created_at
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        query = Product.query.filter(Product.is_active == True)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            query = query.filter(or_(
                Product.name.contains(search),
                Product.description.contains(search),
                Product.brand.contains(search)
            ))
        
        if featured is not None:
            query = query.filter(Product.is_featured == featured)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Apply sorting
        if sort_by == 'name':
            query = query.order_by(Product.name.asc() if sort_order == 'asc' else Product.name.desc())
        elif sort_by == 'price':
            query = query.order_by(Product.price.asc() if sort_order == 'asc' else Product.price.desc())
        elif sort_by == 'rating':
            query = query.order_by(Product.rating.asc() if sort_order == 'asc' else Product.rating.desc())
        else:  # created_at
            query = query.order_by(Product.created_at.asc() if sort_order == 'asc' else Product.created_at.desc())
        
        # Paginate
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    try:
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'categories': [category.to_dict() for category in categories]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/cart', methods=['GET'])
def get_cart():
    """Get user's cart items"""
    try:
        # For demo purposes, using user_id = 1
        # In a real app, you'd get this from authentication
        user_id = 1
        
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        total = sum(item.product.price * item.quantity for item in cart_items if item.product)
        
        return jsonify({
            'success': True,
            'cart_items': [item.to_dict() for item in cart_items],
            'total': total,
            'count': len(cart_items)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'success': False, 'error': 'Product ID is required'}), 400
        
        # Check if product exists
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # For demo purposes, using user_id = 1
        user_id = 1
        
        # Check if item already in cart
        existing_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 0:
            return jsonify({'success': False, 'error': 'Valid quantity is required'}), 400
        
        # For demo purposes, using user_id = 1
        user_id = 1
        
        cart_item = Cart.query.filter_by(id=item_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        if quantity == 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cart updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        # For demo purposes, using user_id = 1
        user_id = 1
        
        cart_item = Cart.query.filter_by(id=item_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

