import flask
import db_session
from users import User
from news import News
from flask import jsonify, request

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/news')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if not news:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'news': news.to_dict(only=(
                'title', 'content', 'user.name', 'is_private', 'img'))
        }
    )


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'email', 'created_date'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:users_id>', methods=['GET'])
def get_one_users(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': users.to_dict(only=('id', 'name', 'email', 'created_date'))
        }
    )


@blueprint.route('/api/news/entertainment')
def get_news_entertainment():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id == 1)
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/for_children')
def get_news_for_children():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id == 5)
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/world')
def get_news_world():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id == 2)
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/our_news')
def get_news_our_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id == 3)
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/computer_tehn')
def get_news_computer_tehn():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.category_id.id == 4)
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name', 'img'))
                 for item in news]
        }
    )
