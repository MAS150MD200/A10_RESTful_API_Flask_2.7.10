__author__ = 'atsvetkov'

# TODO: show current command.
# TODO: Add logging.
# TODO: Write configuration.
# TODO: Backup SLB config to TFTP.
# TODO: Message to HipChat.
# TODO: Alert if we try to remove more than half servers from cluster.

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


def acos_open_session(slb):
    # TODO: ad try here.
    if slb not in SLB_TANGO:
        abort(404)
    c = acos.Client(SLB_TANGO[slb]["ip"], acos.AXAPI_21, SLB_TANGO[slb]["username"], SLB_TANGO[slb]["password"])
    return c


def parse_all_service_groups(srv_grp_dict, srv_grp_name=None, c=None):
    srv_grp_result = {}
    member_server_result = []
    for srv_grp in srv_grp_dict["service_group_list"]:
        if srv_grp_name and srv_grp["name"] == srv_grp_name:
            for member_server in srv_grp["member_list"]:
                # get status of the real server:
                member_server_status = find_server(member_server["server"], c)["server"]["status"]
                member_server_result.append({"server": member_server["server"],
                                             "port": member_server["port"],
                                             "member status": member_server["status"],
                                             "server_status": member_server_status})
            return {srv_grp["name"]: member_server_result}
        srv_grp_result[srv_grp["name"]] = srv_grp["member_list"]
    return srv_grp_result if not srv_grp_name else abort(404)


def find_server(server_name, session):
    server = None
    c = session
    try:
        server = c.slb.server.get(server_name)
    except Exception:
        abort(404)
    return server


# RESTful API:
@app.route('/a10-slb/api/v1.0/<slb>/service-groups', methods=['GET'])
# @auth.login_required
def get_service_groups(slb):
    c = acos_open_session(slb)
    all_service_groups = c.slb.service_group.all()
    c.session.close()

    return jsonify(parse_all_service_groups(all_service_groups))


@app.route('/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>/<result_format>', methods=['GET'])
# @auth.login_required
def get_service_group_member(slb, service_group_name, result_format):

    if result_format not in ["summary", "detailed"]:
        abort(404)

    c = acos_open_session(slb)
    all_service_groups = c.slb.service_group.all()

    if result_format == "detailed":
        srv_grp = parse_all_service_groups(all_service_groups, service_group_name, c)
    elif result_format == "summary":
        all_service_groups = all_service_groups["service_group_list"]
        srv_grp = [grp for grp in all_service_groups if grp["name"] == service_group_name][0]

    c.session.close()

    return jsonify(srv_grp)



@app.route('/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>/<server_name>:<server_port>', methods=['DELETE'])
@auth.login_required
def delete_service_group_member(slb, service_group_name, server_name, server_port):
    c = acos_open_session(slb)
    delete_result = c.slb.service_group.member.delete(service_group_name, server_name, server_port)
    c.session.close()

    return jsonify({"response": delete_result})


@app.route('/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>/<server_name>:<server_port>', methods=['POST'])
@auth.login_required
def create_service_group_member(slb, service_group_name, server_name, server_port):
    c = acos_open_session(slb)
    create_result = c.slb.service_group.member.create(service_group_name,server_name,server_port)
    c.session.close()

    return jsonify({"response": create_result})


@app.route('/a10-slb/api/v1.0/<slb>/server/<server_name>', methods=['GET'])
# @auth.login_required
def server_info(slb, server_name):
    c = acos_open_session(slb)
    server = find_server(server_name, c)
    c.session.close()

    return jsonify(server)


@app.route('/a10-slb/api/v1.0/<slb>/server/<server_name>/status', methods=['GET'])
# @auth.login_required
def get_server_status(slb, server_name):
    # TODO: check if multiple servers with same name and different ip.
    c = acos_open_session(slb)
    server = find_server(server_name, c)
    c.session.close()

    return jsonify({"status": server["server"]["status"]})


@app.route('/a10-slb/api/v1.0/<slb>/server/<server_name>/status/<int:new_status>', methods=['PUT'])
@auth.login_required
def set_server_status(slb, server_name, new_status):
    # TODO: check if multiple servers with same name and different ip.

    if new_status not in [0, 1]:
        abort(404)

    c = acos_open_session(slb)
    server = find_server(server_name, c)
    server_host = server["server"]["host"]

    set_status = c.slb.server.update(server_name, server_host, status=new_status)
    c.session.close()

    return c.http.response_data


if __name__ == '__main__':
    app.run(debug=True)
