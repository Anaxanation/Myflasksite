from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import secrets
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Конфигурация
CONFIG_FILE = 'admin_config.json'
LOG_FILE = 'templates/admin.log'

# Инициализация логгера
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class AdminConfig:
    def __init__(self):
        self.password_hash = generate_password_hash("admin123")
        self.secret_path = f"/admin-{secrets.token_hex(8)}"
        self.products = [
            {
                'id': 1,
                'name': 'Мини бокс',
                'price': 2000,
                'description': 'Компактная коробка',
                'image': 'https://via.placeholder.com/300x300?text=Mini+Box',
                'in_stock': True,
                'category': 'small'
            },
            {
                'id': 2,
                'name': 'Миди бокс',
                'price': 5000,
                'description': 'Средняя коробка',
                'image': 'https://via.placeholder.com/300x300?text=Midi+Box',
                'in_stock': True,
                'category': 'medium'
            }
        ]
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.password_hash = config.get('password_hash', self.password_hash)
                self.products = config.get('products', self.products)

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'password_hash': self.password_hash,
                'products': self.products
            }, f)


# Инициализация конфига
admin_config = AdminConfig()


# Декоратор для проверки админского доступа
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


### Основные маршруты магазина ###
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html',
                           team_members=[
                               {'name': 'Иван Иванов', 'position': 'CEO', 'photo': '...'},
                               {'name': 'Петр Петров', 'position': 'Дизайнер', 'photo': '...'}
                           ])


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Здесь можно добавить отправку email
        flash('Спасибо за сообщение! Мы вам ответим в ближайшее время.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/products')
def products_page():
    return render_template('products.html', products=admin_config.products)


### Корзина ###
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart

    flash('Товар добавлен в корзину!', 'success')
    return redirect(request.referrer or url_for('products_page'))


@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = next((p for p in admin_config.products if p['id'] == int(product_id)), None)
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total

    return render_template('cart.html', cart_items=cart_items, total=total)


### Админ-панель ###
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')

        if check_password_hash(admin_config.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))

        flash('Неверный пароль', 'danger')

    return render_template('admin_login.html')


@app.route(admin_config.secret_path)
def admin_secret_entry():
    session['admin_logged_in'] = True
    return redirect(url_for('admin_panel'))


@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin/panel.html',
                           products=admin_config.products,
                           admin_path=admin_config.secret_path)


@app.route('/admin/products', methods=['GET', 'POST'])
@admin_required
def manage_products():
    if request.method == 'POST':
        # Обработка добавления/редактирования товара
        pass

    return render_template('admin/products.html', products=admin_config.products)


@app.route('/admin/update-stock', methods=['POST'])
@admin_required
def update_stock():
    product_id = int(request.form.get('product_id'))
    in_stock = request.form.get('in_stock') == 'true'

    for product in admin_config.products:
        if product['id'] == product_id:
            product['in_stock'] = in_stock
            admin_config.save_config()
            return jsonify({'success': True})

    return jsonify({'error': 'Product not found'}), 404


@app.route('/admin/change-password', methods=['GET', 'POST'])
@admin_required
def change_admin_password():
    if request.method == 'POST':
        current_pass = request.form.get('current_password')
        new_pass = request.form.get('new_password')
        confirm_pass = request.form.get('confirm_password')

        if not check_password_hash(admin_config.password_hash, current_pass):
            flash('Текущий пароль неверен', 'danger')
        elif new_pass != confirm_pass:
            flash('Пароли не совпадают', 'danger')
        elif len(new_pass) < 8:
            flash('Пароль должен быть не менее 8 символов', 'danger')
        else:
            admin_config.password_hash = generate_password_hash(new_pass)
            admin_config.save_config()
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('admin_panel'))

    return render_template('admin/change_password.html')


if __name__ == '__main__':
    print(f"Секретный URL для входа: {admin_config.secret_path}")
    app.run(debug=True)