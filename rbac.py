from flask import g, request
from flask_rbac import RoleMixin, RBAC, UserMixin
from users import users

# RBAC exempt doesn't quite play nicely
class GWRBAC(RBAC):
    def exempt(self, endpoint=None):
        def decorator(view_func):
            self.acl.exempt(endpoint or view_func.__name__)
            return view_func

        return decorator

rbac = GWRBAC()

###### HACK ############ - Can be written to some sort of file etc and allow editing
# Can get list of view functions via flask_app.view_functions? to allow admin to pick
# and choose?

rules = [
    # (subjects, actions, object) -> can list multiple subjects and multiple methods
    (['IT'], ['GET'], 'test.hello_world'),
    (['marketing'], ['PATCH'], 'test.patch_hello_world'),
    (['superuser'], ['POST'], 'test.post_hello_world')
]

def init_rbac_rules():
    # initialize Rules
    IT = Role('IT')
    marketing = Role('marketing')

    # super user is child? of all Roles. hence anything IT/Marketing can access, superuser
    # can too
    superuser = Role('superuser')
    superuser.add_parents(IT, marketing)

    for subjects, actions, object in rules:
        # hack allow roles before-hand - must specify endpoint (blueprint_name.func_name)
        # these are wrapper but don't use them as wrappers
        rbac.allow(subjects, methods=actions, endpoint=object)(None)

@rbac.as_role_model
class Role(RoleMixin):
    pass

@rbac.as_user_model
class User(UserMixin):
    def __init__(self, user):
        self.roles = set()
        self.username = user['username']

        for role in user['roles']:
            self.add_role(Role(role))

def get_current_user():
    user = users[request.headers.get('authorization', '').split(' ')[-1]]
    g.current_user = User(user)
    return g.current_user

init_rbac_rules()
rbac.set_user_loader(get_current_user)