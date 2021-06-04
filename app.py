from flask import Flask, Blueprint

blueprint = Blueprint('test', __name__)

# ------ ROUTES -----------------
@blueprint.route('/', methods=['GET'])
def hello_world():
    return 'Get Hello, World!'

@blueprint.route('/', methods=['POST'])
def post_hello_world():
    return 'Post hello world!'
# --------------------------------------

app = Flask(__name__)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
