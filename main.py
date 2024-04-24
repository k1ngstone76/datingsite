import datetime

from flask import Flask, render_template, redirect, request, abort, make_response, jsonify
from forms.form_user import RegisterForm, LoginForm
import flask_login
from flask_login import current_user, login_user

from data.ankets import Anceta
from flask_restful import reqparse, abort, Api, Resource


from data.users import User
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/blogs.db")
    session = db_session.create_session()

    an = Anceta(title="ищу парня", content=")))", created_date=datetime.datetime.now())

    session.add(an)
    session.commit()
    app.run()


@app.route("/")
def first_form():
    # db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    #     news = db_sess.query(Anceta).filter(Anceta.user == current_user)
    # else:
    #     news = db_sess.query(Anceta).all()
    return render_template("first_form.html")

# @app.route('/eeee')
# def index():
#     db_sess = db_session.create_session()
#     if current_user.is_authenticated:
#         news = db_sess.query(Anceta).filter(Anceta.user == current_user)
#     else:
#         news = db_sess.query(Anceta).all()


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
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)  # тыц, там session
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)

if __name__ == '__main__':
    main()