from functools import wraps
from flask import request, abort

# docs - https://flask-user.readthedocs.io/en/latest/authorization.html
# adapted from flask_user - https://github.com/lingthio/Flask-User/blob/master/flask_user/decorators.py
def has_roles(*requirements):
    role_names = request.user['roles']

    # ALWAYS ALLOW SU
    if 'superuser' in role_names:
        return True

            # has_role() accepts a list of requirements
    for requirement in requirements:
        if isinstance(requirement, (list, tuple)):
            # this is a tuple_of_role_names requirement
            tuple_of_role_names = requirement
            authorized = False
            for role_name in tuple_of_role_names:
                if role_name in role_names:
                    # tuple_of_role_names requirement was met: break out of loop
                    authorized = True
                    break
            if not authorized:
                return False                    # tuple_of_role_names requirement failed: return False
        else:
            # this is a role_name requirement
            role_name = requirement
            # the user must have this role
            if not role_name in role_names:
                return False                    # role_name requirement failed: return False

    # All requirements have been met: return True
    return True

# USAGE:
# OR operation (['roleA', 'roleB', 'roleC'])
# AND operation ('roleA', 'roleB', 'roleC')

# Advanced usage
# 2. @roles_required('Starving', ['Artist', 'Programmer']) - user is ('Starving' AND (an 'Artist' OR a 'Programmer'))
def roles_required(*role_names):
    def wrapper(view_function):
        @wraps(view_function)
        def decorator(*args, **kwargs):
            if not has_roles(*role_names):
                return abort(403, 'Not enough access')

            return view_function(*args, **kwargs)

        return decorator

    return wrapper