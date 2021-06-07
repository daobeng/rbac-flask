from flask import Flask, Blueprint, request
from users import users

def authenticate_request():
    user = request.headers.get('authorization', '')
    request.user = users[user.split(' ')[-1]]

blueprint = Blueprint('test', __name__)

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
def hello_world():
    return f'GET: Welcome { request.user["username"] }'

@blueprint.route('/', methods=['POST'])
def post_hello_world():
    return f'POST: You posted { request.user["username"] }'
# --------------------------------------


app = Flask(__name__)
blueprint.before_request(authenticate_request)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
