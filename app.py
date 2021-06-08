from flask import Flask, Blueprint, request, g
from rbac import rbac


blueprint = Blueprint('test', __name__)
app = Flask(__name__)

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
# @rbac.allow(['IT'], methods=['GET'], endpoint='test.hello_world')
def hello_world():
    return f'GET: Welcome { g.current_user.username }'

# should use .exempt but it doesn't play nicely with blueprints and simply uses
# the function name
@blueprint.route('/', methods=['POST'])
# @rbac.allow(['superuser'], methods=['POST'], endpoint='test.post_hello_world')
def post_hello_world():
    return f'POST: You posted { g.current_user.username }'

@blueprint.route('/', methods=['PATCH'])
# @rbac.allow(['marketing'], methods=['PATCH'], endpoint='test.patch_hello_world')
def patch_hello_world():
    return f'POST: You patched { g.current_user.username }'

# exempt endpoint so all can access
@blueprint.route('/all', methods=['GET'])
@rbac.exempt(endpoint='test.all_access')
def all_access():
    return f'You can access Me'
# --------------------------------------


app.config['RBAC_USE_WHITE'] = True # use whitelist

rbac.init_app(app)
# Only allowing rules can access the resources.
# This means, all deny rules and rules you did not add cannot access the resources

app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
