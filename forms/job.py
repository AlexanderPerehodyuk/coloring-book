from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from data.users import User
from data import db_session

db_session.global_init("db/mars_db.db")


class AddJobForm(FlaskForm):
    db_sess = db_session.create_session()
    user_list = [' '.join((u.name, u.surname)) for u in db_sess.query(User).all()]
    job = StringField('Название', validators=[DataRequired()])
    team_leader = SelectField('Старший', validators=[DataRequired()],
                              choices=user_list)
    collaborators = StringField('Соучастники', validators=[DataRequired()])

    work_size = IntegerField('Объём работы, ч', validators=[DataRequired()])

    submit = SubmitField('Добавить работу')
