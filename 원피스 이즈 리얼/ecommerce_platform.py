from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
import uuid
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 데이터베이스 초기화
def init_database():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 사용자 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            country TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 카테고리 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            parent_id INTEGER,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )
    ''')
    
    # 상품 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            original_price DECIMAL(10,2),
            category_id INTEGER,
            brand TEXT,
            sku TEXT UNIQUE,
            stock_quantity INTEGER DEFAULT 0,
            min_stock_level INTEGER DEFAULT 5,
            weight DECIMAL(8,2),
            dimensions TEXT,
            image_urls TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_featured BOOLEAN DEFAULT FALSE,
            rating DECIMAL(3,2) DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # 장바구니 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE(user_id, product_id)
        )
    ''')
    
    # 주문 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_number TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending',
            total_amount DECIMAL(10,2) NOT NULL,
            shipping_cost DECIMAL(10,2) DEFAULT 0.00,
            tax_amount DECIMAL(10,2) DEFAULT 0.00,
            discount_amount DECIMAL(10,2) DEFAULT 0.00,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            shipping_address TEXT,
            billing_address TEXT,
            tracking_number TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 주문 상품 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # 리뷰 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            order_id INTEGER,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            title TEXT,
            comment TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            helpful_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (order_id) REFERENCES orders (id),
            UNIQUE(user_id, product_id, order_id)
        )
    ''')
    
    # 위시리스트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE(user_id, product_id)
        )
    ''')
    
    # 쿠폰 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            discount_type TEXT NOT NULL, -- 'percentage' or 'fixed'
            discount_value DECIMAL(10,2) NOT NULL,
            min_order_amount DECIMAL(10,2) DEFAULT 0.00,
            max_discount_amount DECIMAL(10,2),
            usage_limit INTEGER,
            used_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            valid_from TIMESTAMP,
            valid_until TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# 데코레이터: 로그인 필요
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 데코레이터: 관리자 권한 필요
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not user[0]:
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# 샘플 데이터 생성
def create_sample_data():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 관리자 계정 생성
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, full_name, is_admin)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@ecommerce.com', admin_password, 'Administrator', True))
    
    # 일반 사용자 계정
    user_password = generate_password_hash('user123')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, full_name, phone, address, city, postal_code, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('john_doe', 'john@example.com', user_password, 'John Doe', '010-1234-5678', '123 Main St', 'Seoul', '12345', 'South Korea'))
    
    # 카테고리 생성
    categories = [
        ('전자제품', '스마트폰, 노트북, 태블릿 등'),
        ('의류', '남성복, 여성복, 아동복'),
        ('도서', '소설, 전문서적, 만화'),
        ('홈&리빙', '가구, 인테리어, 생활용품'),
        ('스포츠', '운동용품, 아웃도어 장비'),
        ('뷰티', '화장품, 스킨케어, 향수')
    ]
    
    for name, desc in categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', (name, desc))
    
    # 상품 생성
    products = [
        ('iPhone 15 Pro', 'Apple의 최신 스마트폰', 1200000, 1300000, 1, 'Apple', 'IP15P001', 50, 5, 0.2, '146.6 x 70.6 x 8.25 mm', '📱', True, True, 4.8, 1250),
        ('MacBook Air M2', '13인치 MacBook Air', 1500000, 1600000, 1, 'Apple', 'MBA13M2', 30, 3, 1.24, '304 x 215 x 11.3 mm', '💻', True, True, 4.7, 890),
        ('Samsung Galaxy S24', '삼성 갤럭시 최신 모델', 1100000, 1200000, 1, 'Samsung', 'SGS24001', 40, 5, 0.19, '147 x 70.6 x 7.6 mm', '📱', True, False, 4.6, 750),
        ('나이키 에어맥스', '편안한 운동화', 150000, 180000, 5, 'Nike', 'NAM001', 100, 10, 0.8, '280mm', '👟', True, True, 4.5, 2100),
        ('아디다스 트랙수트', '운동복 세트', 120000, 150000, 5, 'Adidas', 'ATS001', 80, 8, 0.6, 'L size', '👕', True, False, 4.3, 450),
        ('해리포터 전집', '7권 세트', 80000, 100000, 3, 'Scholastic', 'HP7SET', 200, 20, 2.5, '세트 박스', '📚', True, True, 4.9, 3200),
        ('소파 3인용', '편안한 패브릭 소파', 800000, 900000, 4, 'IKEA', 'SF3P001', 15, 2, 45.0, '220 x 88 x 85 cm', '🛋️', True, False, 4.4, 180),
        ('다이슨 청소기', '무선 진공청소기', 600000, 700000, 4, 'Dyson', 'DV11001', 25, 3, 2.2, '1257 x 250 x 224 mm', '🧹', True, True, 4.6, 890)
    ]
    
    for product in products:
        cursor.execute('''
            INSERT OR IGNORE INTO products 
            (name, description, price, original_price, category_id, brand, sku, stock_quantity, min_stock_level, weight, dimensions, image_urls, is_active, is_featured, rating, review_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', product)
    
    # 쿠폰 생성
    coupons = [
        ('WELCOME10', '신규 회원 10% 할인', '신규 회원을 위한 특별 할인', 'percentage', 10, 50000, 100000, 1000, 0, True),
        ('SAVE50000', '5만원 할인 쿠폰', '10만원 이상 구매시 5만원 할인', 'fixed', 50000, 100000, None, 500, 0, True),
        ('FREESHIP', '무료배송 쿠폰', '무료배송 혜택', 'fixed', 3000, 30000, 3000, 2000, 0, True)
    ]
    
    for coupon in coupons:
        cursor.execute('''
            INSERT OR IGNORE INTO coupons 
            (code, name, description, discount_type, discount_value, min_order_amount, max_discount_amount, usage_limit, used_count, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', coupon)
    
    conn.commit()
    conn.close()

# 라우트들
@app.route('/')
def index():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 인기 상품
    cursor.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_featured = 1 AND p.is_active = 1 
        ORDER BY p.rating DESC, p.review_count DESC 
        LIMIT 8
    ''')
    featured_products = cursor.fetchall()
    
    # 최신 상품
    cursor.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1 
        ORDER BY p.created_at DESC 
        LIMIT 8
    ''')
    latest_products = cursor.fetchall()
    
    # 카테고리
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    
    conn.close()
    
    return render_template('ecommerce/index.html', 
                         featured_products=featured_products,
                         latest_products=latest_products,
                         categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        
        if not all([username, email, password, full_name]):
            return jsonify({'error': '모든 필수 필드를 입력해주세요.'}), 400
        
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        
        # 중복 확인
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': '이미 존재하는 사용자명 또는 이메일입니다.'}), 400
        
        # 사용자 생성
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, phone))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True})
    
    return render_template('ecommerce/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호를 입력해주세요.'}), 400
        
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, is_admin FROM users WHERE username = ? OR email = ?', (username, username))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            # 로그인 시간 업데이트
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            conn.close()
            
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[3]
            
            return jsonify({'success': True})
        else:
            conn.close()
            return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다.'}), 401
    
    return render_template('ecommerce/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/products')
def products():
    page = int(request.args.get('page', 1))
    per_page = 12
    category_id = request.args.get('category')
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'name')
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 기본 쿼리
    query = '''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.is_active = 1
    '''
    params = []
    
    # 필터링
    if category_id:
        query += ' AND p.category_id = ?'
        params.append(category_id)
    
    if search:
        query += ' AND (p.name LIKE ? OR p.description LIKE ? OR p.brand LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    # 정렬
    if sort_by == 'price_low':
        query += ' ORDER BY p.price ASC'
    elif sort_by == 'price_high':
        query += ' ORDER BY p.price DESC'
    elif sort_by == 'rating':
        query += ' ORDER BY p.rating DESC, p.review_count DESC'
    elif sort_by == 'newest':
        query += ' ORDER BY p.created_at DESC'
    else:
        query += ' ORDER BY p.name ASC'
    
    # 페이징
    offset = (page - 1) * per_page
    query += f' LIMIT {per_page} OFFSET {offset}'
    
    cursor.execute(query, params)
    products_list = cursor.fetchall()
    
    # 전체 개수
    count_query = query.split('ORDER BY')[0].replace('SELECT p.*, c.name as category_name', 'SELECT COUNT(*)')
    cursor.execute(count_query, params[:-2] if 'LIMIT' in query else params)
    total_count = cursor.fetchone()[0]
    
    # 카테고리 목록
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    
    conn.close()
    
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('ecommerce/products.html',
                         products=products_list,
                         categories=categories,
                         current_page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         current_category=category_id,
                         current_search=search,
                         current_sort=sort_by)

if __name__ == '__main__':
    init_database()
    create_sample_data()
    app.run(debug=True, port=5003)
#API 라우트들
@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'error': '상품 ID가 필요합니다.'}), 400
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 상품 존재 확인
    cursor.execute('SELECT id, stock_quantity FROM products WHERE id = ? AND is_active = 1', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return jsonify({'error': '상품을 찾을 수 없습니다.'}), 404
    
    if product[1] < quantity:
        conn.close()
        return jsonify({'error': '재고가 부족합니다.'}), 400
    
    # 장바구니에 추가 또는 업데이트
    cursor.execute('''
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_id) 
        DO UPDATE SET quantity = quantity + ?, added_at = CURRENT_TIMESTAMP
    ''', (session['user_id'], product_id, quantity, quantity))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/cart/count')
@login_required
def get_cart_count():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(quantity) FROM cart_items WHERE user_id = ?', (session['user_id'],))
    count = cursor.fetchone()[0] or 0
    conn.close()
    
    return jsonify({'count': count})

@app.route('/api/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': '상품 ID가 필요합니다.'}), 400
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 상품 존재 확인
    cursor.execute('SELECT id FROM products WHERE id = ? AND is_active = 1', (product_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '상품을 찾을 수 없습니다.'}), 404
    
    # 위시리스트에 추가
    try:
        cursor.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)', 
                      (session['user_id'], product_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': '이미 위시리스트에 있는 상품입니다.'}), 400

@app.route('/cart')
@login_required
def cart():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ci.*, p.name, p.price, p.image_urls, p.stock_quantity, p.brand
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = ?
        ORDER BY ci.added_at DESC
    ''', (session['user_id'],))
    
    cart_items = cursor.fetchall()
    
    # 총 금액 계산
    total_amount = sum(item[3] * item[6] for item in cart_items)  # quantity * price
    
    conn.close()
    
    return render_template('ecommerce/cart.html', 
                         cart_items=cart_items, 
                         total_amount=total_amount)

@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id or quantity < 0:
        return jsonify({'error': '잘못된 요청입니다.'}), 400
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    if quantity == 0:
        # 장바구니에서 제거
        cursor.execute('DELETE FROM cart_items WHERE user_id = ? AND product_id = ?', 
                      (session['user_id'], product_id))
    else:
        # 수량 업데이트
        cursor.execute('''
            UPDATE cart_items 
            SET quantity = ?, added_at = CURRENT_TIMESTAMP 
            WHERE user_id = ? AND product_id = ?
        ''', (quantity, session['user_id'], product_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/checkout')
@login_required
def checkout():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 장바구니 아이템 조회
    cursor.execute('''
        SELECT ci.*, p.name, p.price, p.image_urls, p.stock_quantity, p.brand
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = ?
        ORDER BY ci.added_at DESC
    ''', (session['user_id'],))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('장바구니가 비어있습니다.', 'error')
        return redirect(url_for('cart'))
    
    # 사용자 정보 조회
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # 쿠폰 조회
    cursor.execute('''
        SELECT * FROM coupons 
        WHERE is_active = 1 
        AND (valid_from IS NULL OR valid_from <= CURRENT_TIMESTAMP)
        AND (valid_until IS NULL OR valid_until >= CURRENT_TIMESTAMP)
        AND used_count < usage_limit
    ''')
    available_coupons = cursor.fetchall()
    
    conn.close()
    
    # 금액 계산
    subtotal = sum(item[3] * item[6] for item in cart_items)
    shipping_cost = 3000 if subtotal < 50000 else 0
    tax_amount = subtotal * 0.1  # 10% 세금
    total_amount = subtotal + shipping_cost + tax_amount
    
    return render_template('ecommerce/checkout.html',
                         cart_items=cart_items,
                         user=user,
                         available_coupons=available_coupons,
                         subtotal=subtotal,
                         shipping_cost=shipping_cost,
                         tax_amount=tax_amount,
                         total_amount=total_amount)

@app.route('/api/order/create', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    try:
        # 장바구니 아이템 조회
        cursor.execute('''
            SELECT ci.*, p.name, p.price, p.stock_quantity
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = ?
        ''', (session['user_id'],))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return jsonify({'error': '장바구니가 비어있습니다.'}), 400
        
        # 재고 확인
        for item in cart_items:
            if item[3] > item[7]:  # quantity > stock_quantity
                return jsonify({'error': f'{item[5]} 상품의 재고가 부족합니다.'}), 400
        
        # 주문 번호 생성
        order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"
        
        # 금액 계산
        subtotal = sum(item[3] * item[6] for item in cart_items)
        shipping_cost = 3000 if subtotal < 50000 else 0
        tax_amount = subtotal * 0.1
        discount_amount = 0
        
        # 쿠폰 적용
        coupon_code = data.get('coupon_code')
        if coupon_code:
            cursor.execute('''
                SELECT * FROM coupons 
                WHERE code = ? AND is_active = 1 
                AND (valid_from IS NULL OR valid_from <= CURRENT_TIMESTAMP)
                AND (valid_until IS NULL OR valid_until >= CURRENT_TIMESTAMP)
                AND used_count < usage_limit
            ''', (coupon_code,))
            coupon = cursor.fetchone()
            
            if coupon:
                if subtotal >= coupon[6]:  # min_order_amount
                    if coupon[4] == 'percentage':  # discount_type
                        discount_amount = subtotal * (coupon[5] / 100)
                        if coupon[7]:  # max_discount_amount
                            discount_amount = min(discount_amount, coupon[7])
                    else:  # fixed
                        discount_amount = coupon[5]
                    
                    # 쿠폰 사용 횟수 증가
                    cursor.execute('UPDATE coupons SET used_count = used_count + 1 WHERE id = ?', (coupon[0],))
        
        total_amount = subtotal + shipping_cost + tax_amount - discount_amount
        
        # 주문 생성
        cursor.execute('''
            INSERT INTO orders (user_id, order_number, total_amount, shipping_cost, tax_amount, discount_amount,
                              payment_method, shipping_address, billing_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], order_number, total_amount, shipping_cost, tax_amount, discount_amount,
              data.get('payment_method', 'card'), data.get('shipping_address'), data.get('billing_address')))
        
        order_id = cursor.lastrowid
        
        # 주문 아이템 생성 및 재고 차감
        for item in cart_items:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item[2], item[3], item[6], item[3] * item[6]))
            
            # 재고 차감
            cursor.execute('UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?', 
                          (item[3], item[2]))
        
        # 장바구니 비우기
        cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (session['user_id'],))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'order_number': order_number})
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': '주문 처리 중 오류가 발생했습니다.'}), 500

@app.route('/orders')
@login_required
def orders():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    
    user_orders = cursor.fetchall()
    conn.close()
    
    return render_template('ecommerce/orders.html', orders=user_orders)

@app.route('/order/<order_number>')
@login_required
def order_detail(order_number):
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 주문 정보 조회
    cursor.execute('SELECT * FROM orders WHERE order_number = ? AND user_id = ?', 
                  (order_number, session['user_id']))
    order = cursor.fetchone()
    
    if not order:
        flash('주문을 찾을 수 없습니다.', 'error')
        return redirect(url_for('orders'))
    
    # 주문 아이템 조회
    cursor.execute('''
        SELECT oi.*, p.name, p.image_urls, p.brand
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order[0],))
    
    order_items = cursor.fetchall()
    conn.close()
    
    return render_template('ecommerce/order_detail.html', 
                         order=order, 
                         order_items=order_items)

@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 사용자 정보
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # 최근 주문
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 5
    ''', (session['user_id'],))
    recent_orders = cursor.fetchall()
    
    # 위시리스트
    cursor.execute('''
        SELECT w.*, p.name, p.price, p.image_urls, p.brand
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        WHERE w.user_id = ?
        ORDER BY w.added_at DESC
        LIMIT 10
    ''', (session['user_id'],))
    wishlist_items = cursor.fetchall()
    
    conn.close()
    
    return render_template('ecommerce/profile.html',
                         user=user,
                         recent_orders=recent_orders,
                         wishlist_items=wishlist_items)

# 관리자 라우트들
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # 통계 데이터
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE is_active = 1')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(total_amount) FROM orders WHERE payment_status = "completed"')
    total_revenue = cursor.fetchone()[0] or 0
    
    # 최근 주문
    cursor.execute('''
        SELECT o.*, u.username 
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        LIMIT 10
    ''')
    recent_orders = cursor.fetchall()
    
    # 인기 상품
    cursor.execute('''
        SELECT p.*, SUM(oi.quantity) as total_sold
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT 10
    ''')
    popular_products = cursor.fetchall()
    
    conn.close()
    
    return render_template('ecommerce/admin_dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         popular_products=popular_products)

@app.route('/admin/products')
@admin_required
def admin_products():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.created_at DESC
    ''')
    products_list = cursor.fetchall()
    
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    
    conn.close()
    
    return render_template('ecommerce/admin_products.html',
                         products=products_list,
                         categories=categories)