from flask import Flask, Blueprint, request, g, jsonify, url_for
import casbin
from adapter import ArrayAdapter
from functools import wraps
from users import users

blueprint = Blueprint('test', __name__)

app = Flask(__name__)

# fileadapter
# policy explained, policies at the top
# admin is granted all IT permissions
# admin is granted all marketing permissions (same concept as parents)
# of course this can be put somewhere so admin can modify or so all can be modified in
# one place
rules = [
    # group/policy associations
    # (p - policy, subject, object - url endpoint, action)
    ('p', '','IT', '/', 'GET'),
    ('p', '', 'marketing', '/', '*'),
    ('p', '', 'marketing', '/*', 'GET'),
    ('p', '', 'marketing', '/:id/test', '*'),
    ('p', 'r.sub == r.obj.owner', '*', 'deal', 'delete')

    # group associations
    # (g - group, subject, subject) - a superuser is an IT user as well as marketing user
    # ('g', 'superuser', 'IT'),
    # ('g', 'superuser', 'marketing'),
]

adapter = ArrayAdapter(rules)
casbin_enforcer = casbin.Enforcer('casbinmodel.conf', adapter)


def before_request():
    user = users[request.headers.get('authorization', '').split(' ')[-1]]
    g.current_user = user

# use casbin enforcer as middleware
def enforcer(view_func):

    @wraps(view_func)
    def enforce(*args, **kwargs):
        uri = str(request.path)
        for role in g.current_user['roles']:
            if casbin_enforcer.enforce(role, None, uri, request.method):
                return view_func(*args, **kwargs)
        else:
            user = g.current_user['username']
            app.logger.error(f'Unauthorized attempt: method: { request.method } resource: { uri } by { user }')
            return (jsonify({'message': 'Unauthorized'}), 401)


    return enforce


# enforce roles on special entities
proposal = {
    'name': 'my proposal',
    'price': 25000,
    'owner': 'Mary',
    'casbinType': 'deal',
}

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
@enforcer
def hello_world():
    return f'GET: Welcome { g.current_user["username"] }'

@blueprint.route('/', methods=['POST'])
@enforcer
def post_hello_world():
    return f'POST: You posted { g.current_user["username"] }'

@blueprint.route('/', methods=['PATCH'])
@enforcer
def patch_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/all', methods=['GET'])
@enforcer
def get_all_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/<int:id>/test', methods=['GET'])
@enforcer
def final_one(id):
    return f'POST: { id }'

@blueprint.route('/proposal', methods=['DELETE'])
def get_my_proposal():
    db_proposal = proposal

    # can manually do a superuser check if that's relevant
    if casbin_enforcer.enforce(g.current_user['username'], db_proposal, 'deal', 'delete'):
        return f'Successfully deleted { proposal["name"] }'
    else:
        return (jsonify({'message': 'Unauthorized'}), 401)


@blueprint.route('/site-map', methods=['GET'])
def site_map():
    # can be used to surface endpoints for some minor
    relevant_methods = {'GET', 'PUT', 'POST', 'PATCH', 'DELETE'}

    links = []
    for rule in app.url_map.iter_rules():
        methods = list(rule.methods & relevant_methods)
        links.append((methods, rule.rule))

    return jsonify(links)
# --------------------------------------


app.before_request(before_request)
# app.before_request(casbin_enforcer_middleware)
app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
