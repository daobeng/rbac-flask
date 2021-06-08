from flask import Flask, Blueprint, request, g
from flask_authz import CasbinEnforcer
from adapter import ArrayAdapter
from users import users

blueprint = Blueprint('test', __name__)

app = Flask(__name__)
app.config['CASBIN_MODEL'] = 'casbinmodel.conf'
app.config['CASBIN_OWNER_HEADERS'] = {} # set empty since owner_loader will be provided

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
casbin_enforcer = CasbinEnforcer(app, adapter)
casbin_enforcer.owner_loader(lambda: g.current_user['roles'])

def before_request():
    user = users[request.headers.get('authorization', '').split(' ')[-1]]
    g.current_user = user

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
@casbin_enforcer.enforcer
def hello_world():
    return f'GET: Welcome { g.current_user["username"] }'

@blueprint.route('/', methods=['POST'])
@casbin_enforcer.enforcer
def post_hello_world():
    return f'POST: You posted { g.current_user["username"] }'

@blueprint.route('/', methods=['PATCH'])
@casbin_enforcer.enforcer
def patch_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/all', methods=['GET'])
@casbin_enforcer.enforcer
def get_all_hello_world():
    return f'POST: You patched { g.current_user["username"] }'

@blueprint.route('/<int:id>/test', methods=['GET'])
@casbin_enforcer.enforcer
def final_one(id):
    return f'POST: { id }'
# --------------------------------------


app.before_request(before_request)
app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
