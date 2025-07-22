
from flask import Blueprint, jsonify, request, abort
from src.models.user import User, db
from src.models.product import Product


from functools import wraps
from flask import request, abort

def require_admin_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, "Missing or invalid authorization header")
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if not payload.get("is_admin"):
                abort(403, "Admin access required")
        except jwt.ExpiredSignatureError:
            abort(401, "Token expired")
        except jwt.InvalidTokenError:
            abort(401, "Invalid token")
        return func(*args, **kwargs)
    return wrapper

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    user = User.query.get(user_id)
    return user and getattr(user, "is_admin", False)

@admin_bp.route('/admin/users', methods=['GET'])
def admin_get_users():
    admin_id = request.headers.get('X-Admin-ID')
    if not is_admin(admin_id):
        abort(403)
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@admin_bp.route('/admin/products', methods=['POST'])
def admin_create_product():
    admin_id = request.headers.get('X-Admin-ID')
    if not is_admin(admin_id):
        abort(403)
    data = request.json
    product = Product(name=data['name'], price=data['price'], description=data['description'])
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@admin_bp.route('/admin/products/<int:product_id>', methods=['DELETE'])
def admin_delete_product(product_id):
    admin_id = request.headers.get('X-Admin-ID')
    if not is_admin(admin_id):
        abort(403)
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    user = User.query.filter_by(email=email, is_admin=True).first()
    if not user:
        return jsonify({'error': 'Invalid admin credentials'}), 401
    return jsonify(user.to_dict()), 200

import jwt
import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "mauma_secret_key")

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email, is_admin=True).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'is_admin': True,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({'token': token})
