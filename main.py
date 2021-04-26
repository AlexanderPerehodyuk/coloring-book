import os

from PIL import Image
from flask import Flask, render_template, make_response, jsonify
from werkzeug.utils import redirect
import datetime
from data.users import User
from data.paints import Paints
from data.graphic_redactor import start
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
from data import db_session, paints_api
from flask_restful import Api
from forms.job import AddJobForm
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
@app.route("")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    paints = db_sess.query(Paints).all()
    print(paints)
    links = ['/photo_redactor/' + str(paint.name) for paint in paints]
    print(links)
    user = {u.id: ' '.join((u.name, u.surname)) for u in db_sess.query(User).all()}
    return render_template("index.html", paints=paints, user=user, links=links)


@app.route("/photo_redactor/name")
def redactor(name):
    start(name)
    index()


@app.route('/add_paint', methods=['GET', 'POST'])
def add_job():
    print('adding')
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user_list = {' '.join((u.name, u.surname)): u.id for u in db_sess.query(User).all()}
        paints = Paints(
            name=form.paint.data,
            author=user_list[form.author.data],
            start_date=datetime.datetime.now()
        )
        print(paints, form.photo)
        db_sess.add(paints)
        db_sess.commit()
        try:
            file = open(f'{paints.name}.jpg')
            print(os.path.abspath(f'{paints.name}.jpg'))
            return render_template('add_paint.html', title='Такое название макета уже есть', form=form)
        except FileNotFoundError as e:
            try:
                file = open(f'{paints.name}.jpg', 'w')
                img = Image.open(file)
                img = Image.blend(img, form.photo)
                img.save(f'{paints.name}.jpg')
                print(os.path.abspath(f'{paints.name}.jpg'))
            except Exception as e:
                pass
    return render_template('add_paint.html', title='Добавить фото', form=form)


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
