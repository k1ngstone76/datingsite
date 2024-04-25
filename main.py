import datetime

from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from sqlalchemy.event import api

from forms.form_user import RegisterForm, LoginForm
import flask_login
from flask_login import current_user, login_user, login_manager, login_required, logout_user, LoginManager

from data.ankets import Anceta
from flask_restful import reqparse, abort, Api, Resource


from data.users import User
from data import db_session, ankets_api, ankets_res
from forms.forms_anketa import AncForm

app = Flask(__name__)
api = Api(app)  # создадим объект RESTful-API
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")

    # для списка объектов
    api.add_resource(ankets_res.AnkListResource, '/api/v2/anc')

    # для одного объекта
    api.add_resource(ankets_res.AncResource, '/api/v2/anc/<int:anc_id>')
    app.register_blueprint(ankets_api.blueprint)
    app.run(debug=True)


@app.route('/anketa', methods=['GET', 'POST'])
@login_required
def add_news():
    form = AncForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        anketa = Anceta()
        anketa.title = form.title.data
        anketa.content = form.content.data
        current_user.news.append(anketa)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/all')
    return render_template('anketa.html', title='Добавление анкеты', form=form)


@app.route("/all")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Anceta).all()
        return render_template("index.html", news=news)


@app.route('/anc_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def anc_delete(id):
    db_sess = db_session.create_session()
    anc = db_sess.query(Anceta).filter(Anceta.id == id, Anceta.user == current_user).first()
    if anc:
        db_sess.delete(anc)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/all')


@app.route('/anc/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = AncForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        anc = db_sess.query(Anceta).filter(Anceta.id == id, Anceta.user == current_user).first()
        if anc:
            form.title.data = anc.title
            form.content.data = anc.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        anc = db_sess.query(Anceta).filter(Anceta.id == id, Anceta.user == current_user).first()
        if anc:
            anc.title = form.title.data
            anc.content = form.content.data
            db_sess.commit()
            return redirect('/all')
        else:
            abort(404)
    return render_template('anketa.html', title='Редактирование новости', form=form)


@app.route("/")
def first_form():
    # db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    #     news = db_sess.query(Anceta).filter(Anceta.user == current_user)
    # else:
    #     news = db_sess.query(Anceta).all()
    return render_template("first_form.html")


@app.route('/vibor_reg_or_vxod.html')
def vibor():
    return render_template('vibor_reg_or_vxod.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/all')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/all")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()