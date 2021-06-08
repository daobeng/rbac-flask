from flask import g, request
from flask_rbac import RoleMixin, RBAC, UserMixin
from users import users

rbac = RBAC()

@rbac.as_role_model
class Role(RoleMixin):
    pass

IT = Role('IT')
marketing = Role('marketing')
superuser = Role('superuser')

superuser.add_parents(IT, marketing)

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


rbac.set_user_loader(get_current_user)
