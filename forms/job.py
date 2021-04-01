from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FileField, SubmitField
from wtforms.validators import DataRequired
from data.users import User
from data import db_session

db_session.global_init("db/blogs.db")


class AddJobForm(FlaskForm):
    db_sess = db_session.create_session()
    user_list = [' '.join((u.name, u.surname)) for u in db_sess.query(User).all()]
    paint = StringField('Название', validators=[DataRequired()])
    author = SelectField('Автор', validators=[DataRequired()],
                              choices=user_list)
    photo = FileField('Добавьте фото', validators=[DataRequired()])
    submit = SubmitField('Добавить картинку', validators=[DataRequired()])
