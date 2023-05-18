import os
from io import BytesIO
from os import abort
import requests
from PIL import Image
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import db_session
import news_users_api
from forms.news import NewsForm
from news import News
from users import User
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def latest_news(channel_name):
    telegram_url = 'https://t.me/s/'
    url = telegram_url + channel_name
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    link = soup.find_all("a")
    url = link[-1]['href']
    url = url.replace('https://t.me/', '')
    channel_name, news_id = url.split('/')
    urls = []
    for i in range(7):
        urls.append(f'{channel_name}/{int(news_id) - i}')
    return urls


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_users_api.blueprint)
    app.run()
    # serve(app, host="0.0.0.0", port=8080)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index1():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        f = request.files['f']
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.img:
            os.remove(f'static/img/{user.img}')
        user.img = str(current_user.id) + '.' + str(f.filename.split('.')[-1])
        db_sess.commit()
        image = Image.open(BytesIO(f.read()))
        image.save(f'static/img/{user.img}')

    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True)) \
            .order_by(News.id.desc()).all()
    else:
        news = db_sess.query(News).filter(News.is_private != True).order_by(News.id.desc()).all()
    return render_template("index.html", news=news, lenta='lenta')


@app.route("/news_local", methods=['GET', 'POST'])
def news_local():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route("/categorys/<int:id_category>", methods=['GET', 'POST'])
def categorys(id_category):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id == id_category)
    return render_template('index.html', news=news, lenta="lenta")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if request.method == 'POST':
        if request.form.get('username') \
                and request.form.get('pass1') and request.form.get('pass2'):
            if request.form.get('pass1') != request.form.get('pass2'):
                return render_template('register.html',
                                       message="Пароли не совпадают")
            if '-' in request.form.get('username'):
                return render_template('register.html',
                                       message="В нике недопустимый знак '-'")
            try:
                if request.form.get('name_in_telega'):
                    a = int(request.form.get('name_in_telega'))
                    db_sess = db_session.create_session()
                    user = User(
                        name=request.form.get('username'),
                        name_in_telega=a,
                        img=''
                    )
                else:
                    db_sess = db_session.create_session()
                    user = User(
                        name=request.form.get('username'),
                        img=''
                    )
            except TypeError:
                return render_template('register.html',
                                       message="Не верный формат ID")
            user.set_password(request.form.get('pass1'))
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('name') and request.form.get('pass'):
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.name == request.form.get('name')).first()

            if user and user.check_password(request.form.get('pass')):
                login_user(user)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    bukva = {'1', '2', '3', "4", "5", "6", "7", '8', "9", "0"}
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.category_id = request.form.get('association')
        if request.files['f']:
            f = request.files['f']
            news.img = ''.join(list(bukva)) + '.' + str(f.filename.split('.')[-1])
            image = Image.open(BytesIO(f.read()))
            image.save(f'static/img_news/{news.img}')
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route("/it-tech-tg", methods=["GET"])
def news_page4():
    urls = []
    channel_name = ['it_memes_tg']
    for i in channel_name:
        urls = urls + latest_news(i)
    return render_template('news_telega.html', urls=list(set(urls)))


@app.route("/about-us-tg", methods=["GET"])
def news_page3():
    urls = []
    channel_name = ['Match_TV', "m0NESYGG", 'newsbarcarus']
    for i in channel_name:
        urls = urls + latest_news(i)
    return render_template('news_telega.html', urls=urls)


@app.route("/world-tg", methods=["GET"])
def news_page2():
    urls = []
    channel_name = ['rian_ru', 'toporlive', 'SolovievLive']
    for i in channel_name:
        urls = urls + latest_news(i)
    return render_template('news_telega.html', urls=urls)


@app.route("/memes-tg", methods=["GET"])
def news_page1():
    urls = []
    channel_name = ['mudak', 'ligapsh']
    for i in channel_name:
        urls = urls + latest_news(i)
    return render_template('news_telega.html', urls=urls)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.img = news.img
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.category_id = request.form.get('association')
            news.is_private = form.is_private.data
            if request.files['f']:
                f = request.files['f']
                news.img = str(news.id) + '.' + str(f.filename.split('.')[-1])
                image = Image.open(BytesIO(f.read()))
                image.save(f'static/img_news/{news.img}')
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        if news.img:
            os.remove(f'static/img_news/{news.img}')
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/home_page/<int:id>", methods=["GET", "POST"])
@login_required
def home_page(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", img=current_user.img,
                           your_count=your_count, user_id=id)


@app.route("/home_page/<int:id>/<int:id_category>", methods=["GET", "POST"])
@login_required
def home_page_funny(id, id_category):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id, News.category_id == id_category)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", your_count=your_count, user_id=id)


@app.route('/api/register', methods=['POST'])
def api_register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.name == username):
        user = User(
            name=username
        )
        user.set_password(password)
        db_sess.add(user)
        db_sess.commit()
        response = {
            'message': 'Registration Successful'
        }
        return jsonify(response), 200
    response = {
            'message': 'Such a user already exists'
        }
    return jsonify(response), 404


@app.route('/api/login', methods=['POST'])
def api_login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == username).first()

    if user and user.check_password(password):
        response = {
            'message': 'Registration Successful'
        }
        return jsonify(response), 200
    response = {
            'message': 'Invalid password'
        }
    return jsonify(response), 404




if __name__ == '__main__':
    main()
