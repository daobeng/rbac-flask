from flask import Flask, Blueprint, request, g, jsonify
import casbin
from adapter import ArrayAdapter
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
    ('p', 'IT', '/', 'GET'),
    ('p', 'marketing', '/', '*'),
    ('p', 'marketing', '/*', 'GET'),
    ('p', 'marketing', '/:id/test', '*'),

    # group associations
    # (g - group, subject, subject) - a superuser is an IT user as well as marketing user
    ('g', 'superuser', 'IT'),
    ('g', 'superuser', 'marketing'),
]

adapter = ArrayAdapter(rules)
casbin_enforcer = casbin.Enforcer('casbinmodel.conf', adapter)


def before_request():
    user = users[request.headers.get('authorization', '').split(' ')[-1]]
    g.current_user = user

# use casbin enforcer as middleware
def casbin_enforcer_middleware():
    # enforce permissions if X-EnforcePermissions: true is passed in header as roll out plan
    use_enforcer = request.headers.get('X-EnforcePermissions', '').lower() == 'true'

    if use_enforcer:
        uri = str(request.path)
        for role in g.current_user['roles']:
            if casbin_enforcer.enforce(role, uri, request.method):
                break
        else:
            user = g.current_user['username']
            app.logger.error(f'Unauthorized attempt: method: { request.method } resource: { uri } by { user }')
            return (jsonify({'message': 'Unauthorized'}), 401)


# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
def hello_world():
    return f'GET: Welcome { g.current_user["username"] }'

@blueprint.route('/', methods=['POST'])
def post_hello_world():
    return f'POST: You posted { g.current_user["username"] }'

@blueprint.route('/', methods=['PATCH'])
def patch_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/all', methods=['GET'])
def get_all_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/<int:id>/test', methods=['GET'])
def final_one(id):
    return f'POST: { id }'
# --------------------------------------


app.before_request(before_request)
app.before_request(casbin_enforcer_middleware)
app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
