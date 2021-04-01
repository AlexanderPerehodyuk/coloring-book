import flask
from flask import jsonify, make_response, request
from data.users import User

from . import db_session
from .paints import Paints

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/paints', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    paints = db_sess.query(Paints).all()
    if not paints:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'paints':
                [item.to_dict(only=(
                    'id', 'author', 'name', 'start_date', 'end_date', 'is_finished')) for item in paints]
        }
    )


@blueprint.route('/api/paints/<int:id>', methods=['GET'])
def get_jobs_by_id(id):
    db_sess = db_session.create_session()
    paint = db_sess.query(Paints).get(id)
    if paint is None:
        return make_response(jsonify({'error': 'paint not found'}), 400)
    return jsonify(
        {
            'paint':
                [paint.to_dict(only=(
                    'id', 'author', 'name', 'start_date', 'end_date', 'is_finished'))]
        }
    )


@blueprint.route('/api/paints', methods=['POST'])
def add_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['author', 'name']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()
    try:
        jobs = Paints(**request.json)
    except TypeError as err:
        return make_response(jsonify({'error': str(err)}), 500)
    if db_sess.query(Paints).filter(jobs.id == Paints.id).first():
        return make_response(jsonify({'error': 'Id already exists'}), 400)
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})
