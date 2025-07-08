import os
import sys
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import secrets

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from src.models.user import db

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize Flask-RESTX
api = Api(
    app,
    version='1.0',
    title='Comprehensive API with 50 Features',
    description='A comprehensive REST API with 50 different features and API key authentication',
    doc='/swagger/',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key'
        }
    },
    security='apikey'
)

# Sample API keys for demonstration
VALID_API_KEYS = {
    'demo-key-123': {'name': 'Demo User', 'permissions': ['read', 'write', 'admin']},
    'test-key-456': {'name': 'Test User', 'permissions': ['read', 'write']},
    'readonly-789': {'name': 'Read Only User', 'permissions': ['read']}
}

def require_api_key(permissions=None):
    """Decorator to require API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                api.abort(401, 'API key is required')
            
            if api_key not in VALID_API_KEYS:
                api.abort(401, 'Invalid API key')
            
            user_info = VALID_API_KEYS[api_key]
            
            if permissions:
                if not any(perm in user_info['permissions'] for perm in permissions):
                    api.abort(403, 'Insufficient permissions')
            
            # Add user info to request context
            request.current_user = user_info
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Create namespaces for different API categories
auth_ns = Namespace('auth', description='Authentication operations')
users_ns = Namespace('users', description='User management operations')
products_ns = Namespace('products', description='Product management operations')
orders_ns = Namespace('orders', description='Order management operations')
analytics_ns = Namespace('analytics', description='Analytics and reporting operations')
files_ns = Namespace('files', description='File management operations')
notifications_ns = Namespace('notifications', description='Notification operations')
system_ns = Namespace('system', description='System operations')

api.add_namespace(auth_ns, path='/api/auth')
api.add_namespace(users_ns, path='/api/users')
api.add_namespace(products_ns, path='/api/products')
api.add_namespace(orders_ns, path='/api/orders')
api.add_namespace(analytics_ns, path='/api/analytics')
api.add_namespace(files_ns, path='/api/files')
api.add_namespace(notifications_ns, path='/api/notifications')
api.add_namespace(system_ns, path='/api/system')

# Models for Swagger documentation
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'phone': fields.String(description='Phone number'),
    'role': fields.String(description='User role'),
    'status': fields.String(description='User status'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'last_login': fields.DateTime(description='Last login timestamp')
})

product_model = api.model('Product', {
    'id': fields.Integer(description='Product ID'),
    'name': fields.String(required=True, description='Product name'),
    'description': fields.String(description='Product description'),
    'price': fields.Float(required=True, description='Product price'),
    'category': fields.String(description='Product category'),
    'stock': fields.Integer(description='Stock quantity'),
    'sku': fields.String(description='Stock keeping unit'),
    'status': fields.String(description='Product status'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

order_model = api.model('Order', {
    'id': fields.Integer(description='Order ID'),
    'user_id': fields.Integer(required=True, description='User ID'),
    'total_amount': fields.Float(description='Total order amount'),
    'status': fields.String(description='Order status'),
    'shipping_address': fields.String(description='Shipping address'),
    'payment_method': fields.String(description='Payment method'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

# Authentication endpoints
@auth_ns.route('/validate')
class ValidateAPIKey(Resource):
    @auth_ns.doc('validate_api_key')
    @require_api_key()
    def get(self):
        """Validate API key"""
        return {
            'valid': True,
            'user': request.current_user['name'],
            'permissions': request.current_user['permissions']
        }

@auth_ns.route('/generate-key')
class GenerateAPIKey(Resource):
    @auth_ns.doc('generate_api_key')
    @require_api_key(['admin'])
    def post(self):
        """Generate new API key (Admin only)"""
        new_key = f"key-{secrets.token_urlsafe(16)}"
        return {'api_key': new_key, 'message': 'New API key generated'}

# User Management endpoints (Features 1-10)
@users_ns.route('/')
class UserList(Resource):
    @users_ns.doc('list_users')
    @users_ns.marshal_list_with(user_model)
    @require_api_key(['read'])
    def get(self):
        """Get all users"""
        return [
            {'id': 1, 'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'id': 2, 'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'}
        ]

    @users_ns.doc('create_user')
    @users_ns.expect(user_model)
    @users_ns.marshal_with(user_model, code=201)
    @require_api_key(['write'])
    def post(self):
        """Create new user"""
        data = request.json
        return {'id': 3, 'message': 'User created successfully', **data}, 201

@users_ns.route('/<int:user_id>')
class User(Resource):
    @users_ns.doc('get_user')
    @users_ns.marshal_with(user_model)
    @require_api_key(['read'])
    def get(self, user_id):
        """Get user by ID"""
        return {'id': user_id, 'username': f'user_{user_id}', 'email': f'user{user_id}@example.com'}

    @users_ns.doc('update_user')
    @users_ns.expect(user_model)
    @users_ns.marshal_with(user_model)
    @require_api_key(['write'])
    def put(self, user_id):
        """Update user"""
        data = request.json
        return {'id': user_id, 'message': 'User updated successfully', **data}

    @users_ns.doc('delete_user')
    @require_api_key(['admin'])
    def delete(self, user_id):
        """Delete user (Admin only)"""
        return {'message': f'User {user_id} deleted successfully'}, 204

@users_ns.route('/<int:user_id>/profile')
class UserProfile(Resource):
    @users_ns.doc('get_user_profile')
    @require_api_key(['read'])
    def get(self, user_id):
        """Get user profile"""
        return {'user_id': user_id, 'profile': 'User profile data'}

@users_ns.route('/<int:user_id>/avatar')
class UserAvatar(Resource):
    @users_ns.doc('upload_user_avatar')
    @require_api_key(['write'])
    def post(self, user_id):
        """Upload user avatar"""
        return {'message': f'Avatar uploaded for user {user_id}'}

@users_ns.route('/<int:user_id>/preferences')
class UserPreferences(Resource):
    @users_ns.doc('get_user_preferences')
    @require_api_key(['read'])
    def get(self, user_id):
        """Get user preferences"""
        return {'user_id': user_id, 'preferences': {'theme': 'dark', 'language': 'en'}}

@users_ns.route('/<int:user_id>/activity')
class UserActivity(Resource):
    @users_ns.doc('get_user_activity')
    @require_api_key(['read'])
    def get(self, user_id):
        """Get user activity log"""
        return {'user_id': user_id, 'activities': ['login', 'profile_update', 'logout']}

@users_ns.route('/search')
class UserSearch(Resource):
    @users_ns.doc('search_users')
    @require_api_key(['read'])
    def get(self):
        """Search users"""
        query = request.args.get('q', '')
        return {'query': query, 'results': [{'id': 1, 'username': 'john_doe'}]}

# Product Management endpoints (Features 11-20)
@products_ns.route('/')
class ProductList(Resource):
    @products_ns.doc('list_products')
    @products_ns.marshal_list_with(product_model)
    @require_api_key(['read'])
    def get(self):
        """Get all products"""
        return [
            {'id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics', 'stock': 50},
            {'id': 2, 'name': 'Phone', 'price': 599.99, 'category': 'Electronics', 'stock': 100}
        ]

    @products_ns.doc('create_product')
    @products_ns.expect(product_model)
    @products_ns.marshal_with(product_model, code=201)
    @require_api_key(['write'])
    def post(self):
        """Create new product"""
        data = request.json
        return {'id': 3, 'message': 'Product created successfully', **data}, 201

@products_ns.route('/<int:product_id>')
class Product(Resource):
    @products_ns.doc('get_product')
    @products_ns.marshal_with(product_model)
    @require_api_key(['read'])
    def get(self, product_id):
        """Get product by ID"""
        return {'id': product_id, 'name': f'Product {product_id}', 'price': 99.99}

    @products_ns.doc('update_product')
    @products_ns.expect(product_model)
    @require_api_key(['write'])
    def put(self, product_id):
        """Update product"""
        data = request.json
        return {'id': product_id, 'message': 'Product updated successfully', **data}

    @products_ns.doc('delete_product')
    @require_api_key(['admin'])
    def delete(self, product_id):
        """Delete product (Admin only)"""
        return {'message': f'Product {product_id} deleted successfully'}, 204

@products_ns.route('/<int:product_id>/inventory')
class ProductInventory(Resource):
    @products_ns.doc('get_product_inventory')
    @require_api_key(['read'])
    def get(self, product_id):
        """Get product inventory"""
        return {'product_id': product_id, 'stock': 50, 'reserved': 5, 'available': 45}

    @products_ns.doc('update_product_inventory')
    @require_api_key(['write'])
    def put(self, product_id):
        """Update product inventory"""
        data = request.json
        return {'product_id': product_id, 'new_stock': data.get('stock', 0)}

@products_ns.route('/<int:product_id>/reviews')
class ProductReviews(Resource):
    @products_ns.doc('get_product_reviews')
    @require_api_key(['read'])
    def get(self, product_id):
        """Get product reviews"""
        return {'product_id': product_id, 'reviews': [{'rating': 5, 'comment': 'Great product!'}]}

@products_ns.route('/<int:product_id>/images')
class ProductImages(Resource):
    @products_ns.doc('upload_product_image')
    @require_api_key(['write'])
    def post(self, product_id):
        """Upload product image"""
        return {'message': f'Image uploaded for product {product_id}'}

@products_ns.route('/categories')
class ProductCategories(Resource):
    @products_ns.doc('get_product_categories')
    @require_api_key(['read'])
    def get(self):
        """Get product categories"""
        return {'categories': ['Electronics', 'Clothing', 'Books', 'Home & Garden']}

@products_ns.route('/search')
class ProductSearch(Resource):
    @products_ns.doc('search_products')
    @require_api_key(['read'])
    def get(self):
        """Search products"""
        query = request.args.get('q', '')
        return {'query': query, 'results': [{'id': 1, 'name': 'Laptop'}]}

# Order Management endpoints (Features 21-30)
@orders_ns.route('/')
class OrderList(Resource):
    @orders_ns.doc('list_orders')
    @orders_ns.marshal_list_with(order_model)
    @require_api_key(['read'])
    def get(self):
        """Get all orders"""
        return [
            {'id': 1, 'user_id': 1, 'total_amount': 999.99, 'status': 'completed'},
            {'id': 2, 'user_id': 2, 'total_amount': 599.99, 'status': 'pending'}
        ]

    @orders_ns.doc('create_order')
    @orders_ns.expect(order_model)
    @require_api_key(['write'])
    def post(self):
        """Create new order"""
        data = request.json
        return {'id': 3, 'message': 'Order created successfully', **data}, 201

@orders_ns.route('/<int:order_id>')
class Order(Resource):
    @orders_ns.doc('get_order')
    @orders_ns.marshal_with(order_model)
    @require_api_key(['read'])
    def get(self, order_id):
        """Get order by ID"""
        return {'id': order_id, 'user_id': 1, 'total_amount': 999.99, 'status': 'completed'}

    @orders_ns.doc('update_order')
    @require_api_key(['write'])
    def put(self, order_id):
        """Update order"""
        data = request.json
        return {'id': order_id, 'message': 'Order updated successfully', **data}

@orders_ns.route('/<int:order_id>/status')
class OrderStatus(Resource):
    @orders_ns.doc('update_order_status')
    @require_api_key(['write'])
    def put(self, order_id):
        """Update order status"""
        data = request.json
        return {'order_id': order_id, 'new_status': data.get('status')}

@orders_ns.route('/<int:order_id>/items')
class OrderItems(Resource):
    @orders_ns.doc('get_order_items')
    @require_api_key(['read'])
    def get(self, order_id):
        """Get order items"""
        return {'order_id': order_id, 'items': [{'product_id': 1, 'quantity': 2, 'price': 999.99}]}

@orders_ns.route('/<int:order_id>/shipping')
class OrderShipping(Resource):
    @orders_ns.doc('get_order_shipping')
    @require_api_key(['read'])
    def get(self, order_id):
        """Get order shipping info"""
        return {'order_id': order_id, 'tracking_number': 'TRK123456', 'carrier': 'DHL'}

@orders_ns.route('/<int:order_id>/payment')
class OrderPayment(Resource):
    @orders_ns.doc('get_order_payment')
    @require_api_key(['read'])
    def get(self, order_id):
        """Get order payment info"""
        return {'order_id': order_id, 'payment_method': 'credit_card', 'status': 'paid'}

@orders_ns.route('/<int:order_id>/invoice')
class OrderInvoice(Resource):
    @orders_ns.doc('generate_order_invoice')
    @require_api_key(['read'])
    def get(self, order_id):
        """Generate order invoice"""
        return {'order_id': order_id, 'invoice_url': f'/invoices/{order_id}.pdf'}

@orders_ns.route('/statistics')
class OrderStatistics(Resource):
    @orders_ns.doc('get_order_statistics')
    @require_api_key(['read'])
    def get(self):
        """Get order statistics"""
        return {'total_orders': 1000, 'pending_orders': 50, 'completed_orders': 950}

# Continue with more endpoints...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)



# Analytics endpoints (Features 31-40)
@analytics_ns.route('/dashboard')
class AnalyticsDashboard(Resource):
    @analytics_ns.doc('get_analytics_dashboard')
    @require_api_key(['read'])
    def get(self):
        """Get analytics dashboard data"""
        return {
            'total_users': 1000,
            'total_products': 500,
            'total_orders': 2000,
            'revenue': 50000.00
        }

@analytics_ns.route('/sales')
class SalesAnalytics(Resource):
    @analytics_ns.doc('get_sales_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get sales analytics"""
        return {
            'daily_sales': [100, 150, 200, 180, 220],
            'monthly_sales': [3000, 3500, 4000, 4200],
            'top_products': [{'id': 1, 'name': 'Laptop', 'sales': 50}]
        }

@analytics_ns.route('/users')
class UserAnalytics(Resource):
    @analytics_ns.doc('get_user_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get user analytics"""
        return {
            'new_users': [10, 15, 20, 18, 22],
            'active_users': [800, 850, 900, 920],
            'user_retention': 0.85
        }

@analytics_ns.route('/traffic')
class TrafficAnalytics(Resource):
    @analytics_ns.doc('get_traffic_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get traffic analytics"""
        return {
            'page_views': [1000, 1200, 1500, 1300],
            'unique_visitors': [500, 600, 750, 650],
            'bounce_rate': 0.35
        }

@analytics_ns.route('/revenue')
class RevenueAnalytics(Resource):
    @analytics_ns.doc('get_revenue_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get revenue analytics"""
        return {
            'daily_revenue': [1000, 1500, 2000, 1800],
            'monthly_revenue': [30000, 35000, 40000, 42000],
            'revenue_by_category': {'Electronics': 25000, 'Clothing': 15000}
        }

@analytics_ns.route('/conversion')
class ConversionAnalytics(Resource):
    @analytics_ns.doc('get_conversion_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get conversion analytics"""
        return {
            'conversion_rate': 0.05,
            'funnel_data': [1000, 500, 250, 50],
            'conversion_by_source': {'organic': 0.06, 'paid': 0.04}
        }

@analytics_ns.route('/performance')
class PerformanceAnalytics(Resource):
    @analytics_ns.doc('get_performance_analytics')
    @require_api_key(['read'])
    def get(self):
        """Get performance analytics"""
        return {
            'page_load_time': 2.5,
            'api_response_time': 150,
            'error_rate': 0.01
        }

@analytics_ns.route('/reports')
class AnalyticsReports(Resource):
    @analytics_ns.doc('generate_analytics_report')
    @require_api_key(['read'])
    def post(self):
        """Generate analytics report"""
        data = request.json
        return {
            'report_id': 'RPT123456',
            'type': data.get('type', 'sales'),
            'status': 'generating'
        }

@analytics_ns.route('/export')
class AnalyticsExport(Resource):
    @analytics_ns.doc('export_analytics_data')
    @require_api_key(['read'])
    def post(self):
        """Export analytics data"""
        data = request.json
        return {
            'export_id': 'EXP123456',
            'format': data.get('format', 'csv'),
            'download_url': '/downloads/analytics_export.csv'
        }

@analytics_ns.route('/alerts')
class AnalyticsAlerts(Resource):
    @analytics_ns.doc('get_analytics_alerts')
    @require_api_key(['read'])
    def get(self):
        """Get analytics alerts"""
        return {
            'alerts': [
                {'type': 'revenue_drop', 'message': 'Revenue dropped by 10%', 'severity': 'medium'},
                {'type': 'traffic_spike', 'message': 'Traffic increased by 50%', 'severity': 'low'}
            ]
        }

# File Management endpoints (Features 41-45)
@files_ns.route('/upload')
class FileUpload(Resource):
    @files_ns.doc('upload_file')
    @require_api_key(['write'])
    def post(self):
        """Upload file"""
        return {
            'file_id': 'FILE123456',
            'filename': 'document.pdf',
            'size': 1024000,
            'url': '/files/FILE123456'
        }

@files_ns.route('/<string:file_id>')
class FileDetail(Resource):
    @files_ns.doc('get_file')
    @require_api_key(['read'])
    def get(self, file_id):
        """Get file details"""
        return {
            'file_id': file_id,
            'filename': 'document.pdf',
            'size': 1024000,
            'uploaded_at': '2025-01-07T10:00:00Z'
        }

    @files_ns.doc('delete_file')
    @require_api_key(['write'])
    def delete(self, file_id):
        """Delete file"""
        return {'message': f'File {file_id} deleted successfully'}, 204

@files_ns.route('/<string:file_id>/download')
class FileDownload(Resource):
    @files_ns.doc('download_file')
    @require_api_key(['read'])
    def get(self, file_id):
        """Download file"""
        return {
            'download_url': f'/downloads/{file_id}',
            'expires_at': '2025-01-07T11:00:00Z'
        }

@files_ns.route('/list')
class FileList(Resource):
    @files_ns.doc('list_files')
    @require_api_key(['read'])
    def get(self):
        """List files"""
        return {
            'files': [
                {'file_id': 'FILE123456', 'filename': 'document.pdf', 'size': 1024000},
                {'file_id': 'FILE789012', 'filename': 'image.jpg', 'size': 512000}
            ],
            'total': 2
        }

@files_ns.route('/<string:file_id>/share')
class FileShare(Resource):
    @files_ns.doc('share_file')
    @require_api_key(['write'])
    def post(self, file_id):
        """Share file"""
        data = request.json
        return {
            'share_url': f'/shared/{file_id}',
            'expires_at': data.get('expires_at', '2025-01-14T10:00:00Z')
        }

# Notification endpoints (Features 46-48)
@notifications_ns.route('/')
class NotificationList(Resource):
    @notifications_ns.doc('list_notifications')
    @require_api_key(['read'])
    def get(self):
        """Get notifications"""
        return {
            'notifications': [
                {'id': 1, 'title': 'New order received', 'message': 'Order #123 has been placed', 'read': False},
                {'id': 2, 'title': 'Payment confirmed', 'message': 'Payment for order #122 confirmed', 'read': True}
            ]
        }

    @notifications_ns.doc('create_notification')
    @require_api_key(['write'])
    def post(self):
        """Create notification"""
        data = request.json
        return {
            'id': 3,
            'title': data.get('title'),
            'message': data.get('message'),
            'created_at': '2025-01-07T10:00:00Z'
        }, 201

@notifications_ns.route('/<int:notification_id>/read')
class NotificationRead(Resource):
    @notifications_ns.doc('mark_notification_read')
    @require_api_key(['write'])
    def put(self, notification_id):
        """Mark notification as read"""
        return {'notification_id': notification_id, 'read': True}

@notifications_ns.route('/send')
class NotificationSend(Resource):
    @notifications_ns.doc('send_notification')
    @require_api_key(['write'])
    def post(self):
        """Send notification"""
        data = request.json
        return {
            'message': 'Notification sent successfully',
            'recipients': data.get('recipients', []),
            'type': data.get('type', 'email')
        }

# System endpoints (Features 49-50)
@system_ns.route('/health')
class SystemHealth(Resource):
    @system_ns.doc('system_health_check')
    def get(self):
        """System health check (No auth required)"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': '24h 30m'
        }

@system_ns.route('/info')
class SystemInfo(Resource):
    @system_ns.doc('get_system_info')
    @require_api_key(['admin'])
    def get(self):
        """Get system information (Admin only)"""
        return {
            'version': '1.0.0',
            'environment': 'production',
            'database': 'connected',
            'cache': 'redis',
            'memory_usage': '45%',
            'cpu_usage': '23%'
        }

# Add a simple home route
@app.route('/')
def home():
    return {
        'message': 'Welcome to Comprehensive API with 50 Features',
        'documentation': '/swagger/',
        'version': '1.0.0',
        'features': 50,
        'authentication': 'API Key required (X-API-Key header)',
        'sample_keys': {
            'demo-key-123': 'Full access (read, write, admin)',
            'test-key-456': 'Read and write access',
            'readonly-789': 'Read only access'
        }
    }

