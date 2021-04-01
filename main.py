import os

from flask import Flask, render_template, make_response, jsonify
from werkzeug.utils import redirect
import datetime
from data.users import User
from data.paints import Paints
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
from data import db_session, paints_api
from flask_restful import Api
from data.user_resurce import UsersListResource, UsersResource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'https://www.youtube.com/watch?v=DLzxrzFCyOs'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(paints_api.blueprint)

    api.add_resource(UsersListResource, '/v2/users')
    api.add_resource(UsersResource, '/v2/users/<int:user_id>')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    paints = db_sess.query(Paints).all()
    user = {u.id: ' '.join((u.name, u.surname)) for u in db_sess.query(User).all()}
    return render_template("index.html", paints=paints, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data
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
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
