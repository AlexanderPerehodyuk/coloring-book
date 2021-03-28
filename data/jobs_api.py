import flask
from flask import jsonify, make_response, request
from data.users import User

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    if not jobs:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=(
                    'id', 'team_leader', 'job', 'collaborators', 'work_size',
                    'start_date', 'end_date', 'is_finished')) for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:id>', methods=['GET'])
def get_jobs_by_id(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(id)
    if job is None:
        return make_response(jsonify({'error': 'job not found'}), 400)
    return jsonify(
        {
            'job':
                [job.to_dict(only=(
                    'id', 'team_leader', 'job', 'collaborators', 'work_size',
                    'start_date', 'end_date', 'is_finished'))]
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def add_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'collaborators', 'work_size']):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    db_sess = db_session.create_session()
    try:
        jobs = Jobs(**request.json)
    except TypeError as err:
        return make_response(jsonify({'error': str(err)}), 500)
    if db_sess.query(Jobs).filter(jobs.id == Jobs.id).first():
        return make_response(jsonify({'error': 'Id already exists'}), 400)
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})
