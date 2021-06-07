from flask import Flask, Blueprint, request
from users import users
from decorators import roles_required

def authenticate_request():
    user = request.headers.get('authorization', '')
    request.user = users[user.split(' ')[-1]]

blueprint = Blueprint('test', __name__)

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
@roles_required('IT') # IT only
def hello_world():
    return f'GET: Welcome { request.user["username"] }'

@blueprint.route('/', methods=['POST'])
@roles_required('marketing', 'IT') # marketing and IT
def post_hello_world():
    return f'POST: You posted { request.user["username"] }'

@blueprint.route('/', methods=['PATCH'])
@roles_required(['marketing', 'IT']) # marketing or IT
def patch_hello_world():
    return f'POST: You patched { request.user["username"] }'
# --------------------------------------


app = Flask(__name__)
blueprint.before_request(authenticate_request)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
