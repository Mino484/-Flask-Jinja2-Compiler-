
class ProductManager:
    """Product system manager"""
    
    def __init__(self):
        self.products = []
        self.load_sample_products()
    
    def load_sample_products(self):
        """Load sample products"""
        sample_products = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Dell Laptop',
                'price': 3500.00,
                'description': 'Powerful laptop for work and study',
                'category': 'Electronics',
                'stock': 15,
                'rating': 4.5,
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400',
                'created_at': '2024-01-15'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Samsung Phone',
                'price': 2500.00,
                'description': 'Smartphone with 6.5 inch screen',
                'category': 'Electronics',
                'stock': 25,
                'rating': 4.3,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
                'created_at': '2024-01-10'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Bluetooth Headphones',
                'price': 300.00,
                'description': 'High quality wireless headphones',
                'category': 'Accessories',
                'stock': 50,
                'rating': 4.7,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
                'created_at': '2024-01-05'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Smart Watch',
                'price': 800.00,
                'description': 'Smart watch for fitness tracking',
                'category': 'Electronics',
                'stock': 30,
                'rating': 4.4,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
                'created_at': '2024-01-20'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Canon Camera',
                'price': 4500.00,
                'description': 'Professional camera for photography',
                'category': 'Electronics',
                'stock': 10,
                'rating': 4.8,
                'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400',
                'created_at': '2024-01-18'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Computer Bag',
                'price': 150.00,
                'description': 'Comfortable bag for laptop',
                'category': 'Accessories',
                'stock': 40,
                'rating': 4.2,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
                'created_at': '2024-01-12'
            }
        ]
        self.products = sample_products
    
    def get_all_products(self):
        """Get all products"""
        return self.products
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def add_product(self, product_data):
        """Add new product"""
        product = {
            'id': str(uuid.uuid4()),
            'name': product_data.get('name', 'New Product'),
            'price': float(product_data.get('price', 0)),
            'description': product_data.get('description', ''),
            'category': product_data.get('category', 'General'),
            'stock': int(product_data.get('stock', 0)),
            'rating': float(product_data.get('rating', 0)),
            'image_url': product_data.get('image_url', ''),
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        self.products.append(product)
        return product
    
    def update_product(self, product_id, product_data):
        """Update product"""
        for i, product in enumerate(self.products):
            if product['id'] == product_id:
                for key, value in product_data.items():
                    if key in product:
                        if key in ['price', 'rating']:
                            product[key] = float(value)
                        elif key in ['stock']:
                            product[key] = int(value)
                        else:
                            product[key] = value
                return product
        return None
    
    def delete_product(self, product_id):
        """Delete product"""
        self.products = [p for p in self.products if p['id'] != product_id]
        return True
    
    def search_products(self, query):
        """Search for products"""
        query = query.lower()
        results = []
        for product in self.products:
            if (query in product['name'].lower() or 
                query in product['description'].lower() or 
                query in product['category'].lower()):
                results.append(product)
        return results
    
    def get_products_by_category(self, category):
        """Get products by category"""
        return [p for p in self.products if p['category'] == category]
    
    def get_categories(self):
        """Get list of categories"""
        categories = set()
        for product in self.products:
            categories.add(product['category'])
        return list(categories)

