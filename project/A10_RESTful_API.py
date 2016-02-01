__author__ = 'atsvetkov'

#test

import sys
sys.path.append('./acos_client/')
import acos_client as acos

from config import *

from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

app = Flask(__name__)

@auth.get_password
def get_password(username):
    if username == 'user':
        return 'pass'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def parse_all_service_groups(srv_grp_dict, srv_grp_name=None):
    srv_grp_result = {}
    for srv_grp in srv_grp_dict["service_group_list"]:
        if srv_grp_name and srv_grp["name"] == srv_grp_name:
            return {srv_grp["name"]:srv_grp["member_list"]}
        srv_grp_result[srv_grp["name"]] = srv_grp["member_list"]
    return srv_grp_result if not srv_grp_name else abort(404)


@app.route('/a10-slb/api/v1.0/service-groups', methods=['GET'])
@auth.login_required
def get_service_groups():
    c = acos.Client(a10_ip, acos.AXAPI_21, a10_username, a10_password)
    all_service_groups = c.slb.service_group.all()
    return jsonify(parse_all_service_groups(all_service_groups))


@app.route('/a10-slb/api/v1.0/service-groups/<service_group_name>', methods=['GET'])
@auth.login_required
def get_service_group(service_group_name):
    c = acos.Client(a10_ip, acos.AXAPI_21, a10_username, a10_password)
    all_service_groups = c.slb.service_group.all()
    srv_grp = parse_all_service_groups(all_service_groups, service_group_name)
    return jsonify(srv_grp)



"""
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    # return jsonify({'tasks': tasks})
    return jsonify({'tasks': list(map(make_public_task, tasks))})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})
"""


if __name__ == '__main__':
    app.run(debug=True)