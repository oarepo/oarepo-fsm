"""Permissions and helpers."""
from oarepo_fsm.mixins import FSMMixin


def transition_required(*transitions):
    """
    Permission factory that requires that current user has access to at least one of the transitions and at the same time has ``required`` permission (or factory).

    If the required permission is not set, it is considered as true. If it is callable,
    it is called at first to get the Permission (object with .can() method).
    """

    def factory(record, *_args, **_kwargs):
        def can():
            available_user_transitions = record.available_user_transitions()
            for t in transitions:
                if t in available_user_transitions:
                    return True
            return False

        return type('TransitionRequiredPermission', (), {'can': can})

    return factory


def state_required(*states, state_field=None):
    """
    Permission factory that requires that record is in one of the states. The created permission does not depend on user.

    You can use
    ```
        require_all(state_required('editing'), Permission(RoleNeed('editor')))
    ```
    """
    states = set(states)

    def factory(record, *_args, **_kwargs):
        def can():

            if state_field is None:
                current_state = record._deep_get_state(record)
            else:
                current_state = FSMMixin._deep_get_state(record, state_field.split('.'))

            return current_state in states

        return type('StateRequiredPermission', (), {'can': can})

    return factory


def perm_or_factory(perm, *args, **kwargs):
    """Check if perm is a factory (callable) and if so, apply arguments. If not, just return the perm."""
    if callable(perm):
        return perm(*args, **kwargs)
    return perm


def require_all(*permissions):
    """
    Permission factory that requires that all the permissions are fulfilled - that is, their can() method returns True.

    The permissions might be factories (callable returning the permission). In that case,
    they are called with the arguments and their result is used as a Permission.
    """

    def factory(*args, **kwargs):
        def can(_):
            if not permissions:
                # to behave consistently with require_any
                return False

            for perm in permissions:
                perm = perm_or_factory(perm, *args, **kwargs)
                if not perm.can():
                    return False
            return True

        return type('RequireAllPermission', (), {'can': can})()

    return factory


def require_any(*permissions):
    """
    Permission factory that requires that any the permissions are fulfilled - that is, their can() method returns True.

    The permissions might be factories (callable returning the permission). In that case,
    they are called with the arguments and their result is used as a Permission.
    """

    def factory(*args, **kwargs):
        def can(_):
            for perm in permissions:
                perm = perm_or_factory(perm, *args, **kwargs)
                if perm.can():
                    return True
            return False

        return type('RequireAnyPermission', (), {'can': can})()

    return factory
