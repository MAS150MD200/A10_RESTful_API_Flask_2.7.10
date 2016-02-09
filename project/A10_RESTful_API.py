__author__ = 'atsvetkov'

# TODO: show current command.

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

# global connection variable:
c = None

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


def acos_connect():
    # TODO: ad try here.
    global c;
    c = acos.Client(a10_ip, acos.AXAPI_21, a10_username, a10_password)

def parse_all_service_groups(srv_grp_dict, srv_grp_name=None):
    srv_grp_result = {}
    for srv_grp in srv_grp_dict["service_group_list"]:
        if srv_grp_name and srv_grp["name"] == srv_grp_name:
            return {srv_grp["name"]:srv_grp["member_list"]}
        srv_grp_result[srv_grp["name"]] = srv_grp["member_list"]
    return srv_grp_result if not srv_grp_name else abort(404)


def find_server(server_name):
    server = None
    try:
        server = c.slb.server.get(server_name)
    except Exception:
        abort(404)
    return server


# RESTful API:
@app.route('/a10-slb/api/v1.0/service-groups', methods=['GET'])
@auth.login_required
def get_service_groups():
    all_service_groups = c.slb.service_group.all()
    return jsonify(parse_all_service_groups(all_service_groups))


@app.route('/a10-slb/api/v1.0/service-groups/<service_group_name>', methods=['GET'])
@auth.login_required
def get_service_group_member(service_group_name):
    all_service_groups = c.slb.service_group.all()
    srv_grp = parse_all_service_groups(all_service_groups, service_group_name)
    return jsonify(srv_grp)


@app.route('/a10-slb/api/v1.0/service-groups/<service_group_name>/<server_name>:<server_port>', methods=['DELETE'])
@auth.login_required
def delete_service_group_member(service_group_name, server_name, server_port):
    delete_result = c.slb.service_group.member.delete(service_group_name, server_name, server_port)
    return jsonify({"response": delete_result})


@app.route('/a10-slb/api/v1.0/service-groups/<service_group_name>/<server_name>:<server_port>', methods=['POST'])
@auth.login_required
def create_service_group_member(service_group_name, server_name, server_port):
    create_result = c.slb.service_group.member.create(service_group_name,server_name,server_port)
    return jsonify({"response": create_result})


@app.route('/a10-slb/api/v1.0/server/<server_name>', methods=['GET'])
@auth.login_required
def server_info(server_name):
    server = find_server(server_name)
    return jsonify(server)


@app.route('/a10-slb/api/v1.0/server/<server_name>/status', methods=['GET'])
@auth.login_required
def get_server_status(server_name):
    # TODO: check if multiple servers with same name and different ip.
    server = find_server(server_name)
    return jsonify({"status": server["server"]["status"]})


@app.route('/a10-slb/api/v1.0/server/<server_name>/status/<int:new_status>', methods=['PUT'])
@auth.login_required
def set_server_status(server_name, new_status):
    # TODO: check if multiple servers with same name and different ip.

    if new_status not in [0, 1]:
        abort(404)

    server = find_server(server_name)
    server_host = server["server"]["host"]

    set_status = c.slb.server.update(server_name, server_host, status=new_status)
    return c.http.response_data


if __name__ == '__main__':
    acos_connect()
    app.run(debug=True)