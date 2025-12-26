import email
import json

from datetime import date
from random import randint

from flask import Blueprint, flash, redirect, request, render_template, url_for, g
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, RadioField, HiddenField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from db.database import session_scope
from db.models import User, Book, CartItem, Order, OrderItem, OrderItemTmp, Review
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import or_,func

main_blueprint = Blueprint("main", __name__)

#--------------ДОБАВИТЬ КНИГУ В БАЗУ ДАННЫХ---------------
def add_book(book):
    with session_scope() as session:
        if not session.query(Book).filter_by(title=book['title'],author=book['author']).first():
            session.add(Book(
            title=book['title'].lower(),
            author=book['author'].lower(),
            cover=book['cover'],
            year=book['year'],
            price = book['price'],
            genre = book['genre'].lower(),
#            rating = book['rating'],
            description = book['description']
            ))
        else:
            print('Ошибка: книга с таким автором и названием уже есть в базе.')

#--------------ДОБАВИТЬ КНИГИ В БАЗУ ИЗ ФАЙЛА JSON---------------
def load_from_file(filename):
    with open(filename, 'r',encoding='utf8') as file:
        books_catalog = json.load(file)
    for book_ in books_catalog:
        add_book(book_)

#load_from_file('books_catalog.json')

# Удалить все книги:
# with session_scope() as session:
#     session.query(Book).filter(Book.id != '').delete()

#--------------ФОРМЫ---------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Пароль", validators=[InputRequired(), Length(min=8, max=36)]
    )

class RegistrationForm(FlaskForm):
    name = StringField(
        "Имя", validators=[InputRequired(), Length(max=100, min=3)]
    )
    phone = StringField("Номер телефона в формате +7 (111) 111-11-11", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Пароль", validators=[InputRequired(), Length(min=8, max=36)]
    )
    confirm_password = PasswordField(
        "Повторите пароль", validators=[InputRequired(), Length(min=8, max=36), EqualTo("password")]
    )
    confirm_phone = StringField("Код подтверждения", validators=[InputRequired(), Length(max=4, min=4)])
    code = StringField()

class OrderForm(FlaskForm):
    delivery = RadioField("Выберите способ доставки:", choices=[('pickup', 'самовывоз'), ('door', 'до двери')], validators=[InputRequired()])
    address = StringField("Введите свой адрес:", validators=[Length(max=500)])
    pick_up = SelectField("Выберите пункт выдачи:", choices=[('пункт выдачи 1', 'пункт выдачи 1'), ('пункт выдачи 2', 'пункт выдачи 2'), ('пункт выдачи 3', 'пункт выдачи 3')])
    final_price = StringField()

#--------------ЖАНРЫ---------------
genres = {
    'fiction':['Художественная литература',{
        'contemporary-foreign': 'зарубежная современная литература',
        'classic-foreign': 'зарубежная классическая литература',
        'contemporary-russian': 'русская современная литература',
        'classic-russian': 'русская классическая литература',
        'science-fiction': 'фантастика',
        'fantasy': 'фэнтези',
        'adventure': 'приключения',
        'detective': 'детектив',
        'novel': 'роман',
        'belarusian': 'белорусская литература'
    }],
    'non-fiction': ['Нехудожественная литература',{
        'history': 'история',
        'scientific': 'научная литература',
        'popular-science': 'научно-популярная литература',
        'home-cooking': 'домашний мир, кулинария',
        'travel': 'путеводители, карты, ПДД',
        'foreign-languages': 'иностранные языки',
        'creativity': 'творчество',
        'self-development': 'саморазвитие',
        'IT-literature': 'айти-литература',
        'beauty-sports-nutrition': 'красота, спорт, питание'
    }],
    'for-children': ['Детская литература',{
        'children-fiction': 'детская художественная литература',
        'educational': 'развивающая литература',
        'encyclopedias': 'энциклопедии',
        'interactive': 'интерактивные, игровые книги',
        'for-parents': 'книги для родителей'
    }],
    'business': ['Бизнес-литература',{
        'career': 'саморазвитие, карьера',
        'management': 'менеджмент, управление',
        'marketing': 'маркетинг, реклама',
        'success-stories': 'истории успеха',
        'entrepreneurship': 'предпринимательство'
    }],
    'for-school': ['Учебная литература',{
        'exam-preparation': 'подготовка к экзаменам и ЦТ',
        'workbooks': 'рабочие тетради для школьников'
    }],
    'foreign-books': ['Книги на иностранном языке',{
        'english': 'английский',
        'french': 'французский',
        'german': 'немецкий'
    }],
    'comics-manga-artbooks': ['Комиксы, манга, артбуки',{
        'comics': 'комиксы',
        'manga': 'манга',
        'artbooks': 'артбуки'
    }]
}

@main_blueprint.context_processor
def inject_genres():
    return dict(genres=genres)

@main_blueprint.context_processor
def utility_processor():
    def convert_to_star(num, rating):
        if num > round(rating+0.2, 1):
            if round(num-rating, 1) > 0.7:
                return "bi-star"
            return "bi-star-half"
        return "bi-star-fill"
    return dict(convert_to_star=convert_to_star)

#--------------ГЛАВНАЯ---------------
@main_blueprint.route("/")
def main_route():
    books_list = []
    with session_scope() as session:
        books = session.query(Book).filter(Book.id != '').order_by(Book.rating.desc()).limit(3).all()
        for book in books:
            session.expunge(book)
            books_list.append(book)
    return render_template("home.html", top3=books_list)

#--------------РЕГИСТРАЦИЯ---------------
@main_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    code = str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9))
    if form.validate_on_submit():
        if form.confirm_phone.data != form.code.data:
            flash("Ошибка: Неверный код подтверждения.", 'danger')
            return redirect(url_for("main.register"))
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            flash("Ошибка: Аккаунт с такой почтой уже существует.", 'danger')
            return redirect(url_for("main.register"))
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            password_hash=generate_password_hash(form.password.data),
        )
        with session_scope() as session:
            session.add(user)
        return redirect(url_for("main.login"))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template("register.html", form=form, code=code)

#--------------ВХОД---------------
@main_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('main.main_route'))
        flash('Login failed', 'danger')
    elif form.errors:
        flash(form.errors, 'danger')
    return render_template('login.html', form=form)

#--------------ВЫХОД---------------
@main_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

#--------------РАЗДЕЛЫ---------------
@main_blueprint.route("/section/<section>")
def show_section(section):
    books_list = []
    with session_scope() as session:
        books = session.query(Book).filter(Book.genre.in_(genres[section][1].values())).all()
        for book in books:
            session.expunge(book)
            books_list.append(book)
    return render_template("section.html", title=genres[section][0], books_list=books_list, section=section, placeholder='Тут пока ничего нет.')

#--------------ПОДРАЗДЕЛЫ---------------
@main_blueprint.route("/<section>/<subsection>")
def show_subsection(section,subsection):
    books_list = []
    with session_scope() as session:
        books = session.query(Book).filter_by(genre=genres[section][1][subsection]).all()
        for book in books:
            session.expunge(book)
            books_list.append(book)
    return render_template("section.html", title=genres[section][1][subsection].capitalize(), books_list=books_list, section=section, subsection=subsection, placeholder='Тут пока ничего нет.')

#--------------ИНФОРМАЦИЯ О КНИГЕ---------------
@main_blueprint.route('/book/<int:id>')
def book_info(id):
    is_in_cart = False
    review_list = []
    with session_scope() as session:
        if current_user.is_authenticated:
            is_in_cart = session.query(CartItem).filter_by(user_id=current_user.id, book_id=id).first()
        book = session.query(Book).get(id)
        authors_list = {}
        for review in book.reviews:
            author = review.author
            session.expunge(author)
            authors_list[review.id]=author
            session.expunge(review)
            review = review.__dict__
            review_list.append(review)
        session.expunge(book)
    return render_template('book.html', book=book, is_in_cart=is_in_cart, review_list=review_list, authors_list=authors_list)

#--------------ОТАВИТЬ ОТЗЫВ---------------
@main_blueprint.route('/add-review/<int:id>', methods=["POST"])
@login_required
def add_review(id):
    with session_scope() as session:
        book = session.query(Book).get(id)
        new_rating = (book.rating * len(book.reviews) + float(request.form['rating'])) / (len(book.reviews) + 1)
        session.query(Book).filter_by(id=id).update({'rating': round(new_rating, 1)})
        new_review = Review(
            author=current_user,
            book=book,
            content=request.form['content'],
            rating=request.form['rating']
        )
        session.add(new_review)
    return redirect(url_for("main.book_info", id=id))

#--------------ДОБАВИТЬ В КОРЗИНУ---------------
@main_blueprint.route("/add-to-cart/<int:id>")
@login_required
def add_to_cart(id):
    with session_scope() as session:
        b = session.query(Book).get(id)
        session.add(CartItem(owner=current_user,added_book=b))
    return redirect(url_for('main.book_info', id=id))

#--------------КОРЗИНА---------------
@main_blueprint.route("/cart")
@login_required
def cart():
    items_list = []
    with session_scope() as session:
        u = session.query(User).get(current_user.id)
        for item in u.cart_items:
            book = item.added_book
            session.expunge(book)
            book = book.__dict__
            book['amount'] = item.amount
            book['item_id'] = item.id
            items_list.append(book)
    return render_template("cart.html", items_list=items_list)

#--------------ИЗМЕНИТЬ КОЛ-ВО КНИГ---------------
@main_blueprint.route("/change_amount/<int:id>")
def change_amount(id):
    new_amount = request.args.get('new_amount')
    with session_scope() as session:
        session.query(CartItem).filter_by(id=id).update({'amount': new_amount})
    return redirect(url_for('main.cart'))

#--------------УДАЛИТЬ ИЗ КОРЗИНЫ---------------
@main_blueprint.route('/delete-from-cart/<int:id>')
@login_required
def delete_from_cart(id):
    with session_scope() as session:
        session.query(CartItem).filter_by(id=id).delete()
    return redirect(url_for('main.cart'))

#--------------ОФОРМИТЬ ЗАКАЗ---------------
@main_blueprint.route("/new-order", methods=["GET", "POST"])
@login_required
def new_order():
    form = OrderForm()
    item_ids = request.form.getlist("item_id")
    if item_ids:
        with session_scope() as session:
            session.query(OrderItemTmp).filter_by(user_id=current_user.id).delete()
            for id in item_ids:
                item = session.query(CartItem).get(id)
                book = item.added_book
                session.expunge(book)
                book = book.__dict__
                book['amount'] = item.amount
                book['item_id'] = item.id
                order_item_tmp = OrderItemTmp(
                    id=item.id,
                    user_id=current_user.id,
                    added_book=item.added_book,
                    amount=item.amount,
                    book_dict=book
                )
                session.add(order_item_tmp)
    elif form.validate_on_submit():
        address = ''
        if form.delivery.data == 'pickup':
            address = form.pick_up.data
        elif form.address.data.strip():
            address = form.address.data.strip()
        else:
            flash('Ошибка: Некорректный адрес', category='danger')
        if address:
            order = Order(
                owner=current_user,
                date=date.today(),
                status='в пути',
                address=address,
                price=form.final_price.data
            )
            with session_scope() as session:
                order_items_tmp = session.query(OrderItemTmp).filter_by(user_id=current_user.id).all()
                if order_items_tmp:
                    session.add(order)
                    for item_tmp in order_items_tmp:
                        order_item = OrderItem(
                            order=order,
                            added_book=item_tmp.added_book,
                            amount=item_tmp.amount,
                        )
                        session.add(order_item)
                        session.query(CartItem).filter_by(id=item_tmp.id).delete()
                    session.query(OrderItemTmp).filter_by(user_id=current_user.id).delete()
            return render_template("success.html", text='Ваш заказ успешно оформлен!')
    elif form.errors:
        flash(form.errors, category='danger')
    items_list = []
    final_price = 0
    with session_scope() as session:
        order_items_tmp = session.query(OrderItemTmp).filter_by(user_id=current_user.id).all()
        for item_tmp in order_items_tmp:
            final_price += int(item_tmp.book_dict['amount']) * float(item_tmp.book_dict['price'])
            items_list.append(item_tmp.book_dict)
    return render_template("new_order.html", form=form, items_list=items_list, final_price=round(final_price, 2))

#--------------УДАЛИТЬ ИЗ ЗАКАЗА---------------
@main_blueprint.route('/delete-order-item/<int:id>')
@login_required
def delete_order_item(id):
    with session_scope() as session:
        session.query(OrderItemTmp).filter_by(id=id).delete()
    return redirect(url_for('main.new_order'))

#--------------ЗАКАЗЫ---------------
@main_blueprint.route("/orders")
@login_required
def orders():
    orders_list = []
    orders_items = {}
    with session_scope() as session:
        u = session.query(User).get(current_user.id)
        for order in u.orders:
            book_list = []
            for item in order.items_list:
                name_amount = []
                book = item.added_book
                session.expunge(book)
                name_amount.append(book)
                name_amount.append(item.amount)
                book_list.append(name_amount)
            orders_items[order.id] = book_list
            session.expunge(order)
            orders_list.append(order)
    return render_template("orders.html", orders_list=orders_list,orders_items=orders_items)

#--------------ОТМЕНИТЬ ЗАКАЗ---------------
@main_blueprint.route('/cancel-order/<int:id>')
@login_required
def cancel_order(id):
    with session_scope() as session:
        session.query(OrderItem).filter_by(order_id=id).delete()
        session.query(Order).filter_by(id=id).delete()
    return render_template("success.html", text=f'Заказ №{id} успешно отменён.')

#--------------ПОИСК---------------
@main_blueprint.route('/search')
def search():
    books_list = []
    search_query = request.args.get('query').lower()
    if search_query.strip():
        with session_scope() as session:
            books = session.query(Book).filter(or_(Book.author.contains(search_query), Book.title.contains(search_query), Book.genre.contains(search_query))).all()
            print(books)
            for book in books:
                session.expunge(book)
                books_list.append(book)
    return render_template("section.html", title="Результаты поиска:", books_list=books_list, placeholder='Что бы вы ни искали, у нас этого нет.')







