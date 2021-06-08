from flask import Flask, Blueprint, request, g
from rbac import rbac


blueprint = Blueprint('test', __name__)


# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
@rbac.allow(['IT'], methods=['GET'], endpoint='test.hello_world')
def hello_world():
    return f'GET: Welcome { g.current_user.username }'

@blueprint.route('/', methods=['POST'])
@rbac.allow(['anonymous'], methods=['POST'], endpoint='test.post_hello_world')
def post_hello_world():
    return f'POST: You posted { g.current_user.username }'

@blueprint.route('/', methods=['PATCH'])
@rbac.allow(['marketing'], methods=['PATCH'], endpoint='test.patch_hello_world')
def patch_hello_world():
    return f'POST: You patched { g.current_user.username }'
# --------------------------------------


app = Flask(__name__)

app.config['RBAC_USE_WHITE'] = True # use whitelist

rbac.init_app(app)
# Only allowing rules can access the resources.
# This means, all deny rules and rules you did not add cannot access the resources

app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
