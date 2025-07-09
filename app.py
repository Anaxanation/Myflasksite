from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_bootstrap import Bootstrap
from math import ceil
import re
from datetime import datetime
import json
import os

orders_db = []



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Замените на реальный ключ!
Bootstrap(app)

# Данные товаров
products = [
    {
        'id': 1,
        'name': 'Мини бокс',
        'price': 2000,
        'description': 'Компактная коробка для небольших предметов',
        'image': 'https://via.placeholder.com/300x300?text=Mini+Box',
        'in_stock': True,
        'category': 'small'
    },
    {
        'id': 2,
        'name': 'Миди бокс',
        'price': 5000,
        'description': 'Средняя коробка для повседневного использования',
        'image': 'https://via.placeholder.com/300x300?text=Midi+Box',
        'in_stock': False,
        'category': 'medium'
    },
    {
        'id': 3,
        'name': 'Макси бокс',
        'price': 10000,
        'description': 'Большая коробка для хранения вещей',
        'image': 'https://via.placeholder.com/300x300?text=Maxi+Box',
        'in_stock': True,
        'category': 'large'
    }
]


@app.route('/')
def index():
    return render_template('index.html', title='Главная')


team_members = [
    {
        'id': 1,
        'name': 'Иван Иванов',
        'position': 'Главный разработчик',
        'bio': 'Специалист с 10-летним опытом в веб-разработке.',
        'photo': 'https://via.placeholder.com/300x300?text=Team+1'
    },
    {
        'id': 2,
        'name': 'Петр Петров',
        'position': 'Дизайнер',
        'bio': 'Создаёт удобные и красивые интерфейсы.',
        'photo': 'https://via.placeholder.com/300x300?text=Team+2'
    },
    {
        'id': 3,
        'name': 'Сергей Сергеев',
        'position': 'Менеджер проектов',
        'bio': 'Координирует работу команды и общается с клиентами.',
        'photo': 'https://via.placeholder.com/300x300?text=Team+3'
    },
    {
        'id': 4,
        'name': 'Анна Смирнова',
        'position': 'Маркетолог',
        'bio': 'Продвигает наши продукты на рынке.',
        'photo': 'https://via.placeholder.com/300x300?text=Team+4'
    },
    {
        'id': 5,
        'name': 'Дмитрий Кузнецов',
        'position': 'Тестировщик',
        'bio': 'Обеспечивает качество наших продуктов.',
        'photo': 'https://via.placeholder.com/300x300?text=Team+5'
    }
]

@app.route('/about')
def about():
    return render_template('about.html', team=team_members, title='О нас')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', title='Контакты')


@app.route('/products')
def products_page():
    page = request.args.get('page', 1, type=int)
    per_page = 4
    category = request.args.get('category', None)

    filtered_products = products
    if category:
        filtered_products = [p for p in products if p.get('category') == category]

    total_pages = ceil(len(filtered_products) / per_page)
    paginated_products = filtered_products[(page - 1) * per_page: page * per_page]

    return render_template('products.html',
                           products=paginated_products,
                           current_page=page,
                           total_pages=total_pages,
                           current_category=category,
                           title='Наши товары')


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return 0
    return render_template('product_detail.html', product=product)


# Корзина
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
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total

    return render_template('cart.html', cart_items=cart_items, total=total, title='Корзина')


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart

    flash('Товар удален из корзины', 'info')
    return redirect(url_for('view_cart'))


@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)
    cart = session.get('cart', {})

    if quantity > 0:
        cart[str(product_id)] = quantity
    else:
        cart.pop(str(product_id), None)

    session['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Проверяем, что корзина не пуста
    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста!', 'warning')
        return redirect(url_for('view_cart'))

    # Получаем товары из корзины
    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total

    # Обработка формы
    if request.method == 'POST':
        # Получаем данные
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        comment = request.form.get('comment', '').strip()

        # Валидация
        errors = False

        if not name:
            flash('Укажите ваше имя', 'danger')
            errors = True

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Укажите корректный email', 'danger')
            errors = True

        if not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', phone):
            flash('Укажите корректный телефон', 'danger')
            errors = True

        if not address:
            flash('Укажите адрес доставки', 'danger')
            errors = True

        if errors:
            return redirect(url_for('checkout'))

        # Формируем заказ
        order = {
            'id': len(orders_db) + 1,
            'customer': {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'comment': comment
            },
            'items': [],
            'total': total,
            'status': 'new',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Добавляем товары
        for item in cart_items:
            order['items'].append({
                'product_id': item['product']['id'],
                'name': item['product']['name'],
                'price': item['product']['price'],
                'quantity': item['quantity'],
                'subtotal': item['total']
            })

        # Сохраняем заказ (в реальном проекте - в БД)
        orders_db.append(order)

        # Очищаем корзину
        session.pop('cart', None)

        # Отправляем уведомление (заглушка)
        send_order_notification(order)

        flash('Заказ успешно оформлен! Номер вашего заказа: #{}'.format(order['id']), 'success')
        return redirect(url_for('order_confirmation', order_id=order['id']))

    # GET запрос - показываем форму
    return render_template('checkout.html',
                           cart_items=cart_items,
                           total=total,
                           title='Оформление заказа')


def send_order_notification(order):
    """Заглушка для отправки уведомлений"""
    print(f"Новый заказ #{order['id']}")
    print(f"Клиент: {order['customer']['name']}")
    print(f"Телефон: {order['customer']['phone']}")
    print(f"Сумма: {order['total']} руб.")
    # Здесь можно добавить реальную отправку email/SMS


@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    """Страница подтверждения заказа"""
    order = next((o for o in orders_db if o['id'] == order_id), None)
    if not order:
        flash('Заказ не найден', 'danger')
        return redirect(url_for('index'))

    return render_template('order_confirmation.html',
                           order=order,
                           title='Подтверждение заказа')




if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = '5000')
