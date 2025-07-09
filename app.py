from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from math import ceil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Замените на реальный ключ
Bootstrap(app)

# Данные товаров (добавлено поле category)
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
    },
    {
        'id': 4,
        'name': 'Гранде бокс',
        'price': 15999,
        'description': 'Очень большая коробка премиум-класса',
        'image': 'https://via.placeholder.com/300x300?text=Grande+Box',
        'in_stock': True,
        'category': 'premium'
    },
    {
        'id': 5,
        'name': 'Венти бокс',
        'price': 23999,
        'description': 'Коробка с вентиляцией для специальных нужд',
        'image': 'https://via.placeholder.com/300x300?text=Venti+Box',
        'in_stock': True,
        'category': 'special'
    },
    {
        'id': 6,
        'name': 'Мега бокс',
        'price': 45999,
        'description': 'Огромная коробка для промышленного использования',
        'image': 'https://via.placeholder.com/300x300?text=Mega+Box',
        'in_stock': True,
        'category': 'industrial'
    }
]


@app.route('/')
def index():
    return render_template('index.html', title='Главная')


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Здесь можно добавить обработку формы
        flash('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', title='Контакты')


@app.route('/products')
def products_page():
    page = request.args.get('page', 1, type=int)
    per_page = 4  # Товаров на странице
    category = request.args.get('category', None)

    # Фильтрация по категории если указана
    filtered_products = products
    if category:
        filtered_products = [p for p in products if p.get('category') == category]

    # Пагинация
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
        abort(404)
    return render_template('product_detail.html', product=product)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
