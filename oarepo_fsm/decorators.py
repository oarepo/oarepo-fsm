#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from oarepo_fsm.errors import InvalidPermissionError, \
    InvalidSourceStateError, MissingRequiredParameterError


def has_permission(f):
    """Decorator to check the transition permission requirements are fulfilled."""

    def inner(self, record, **kwargs):
        if self.permission and not self.permission(record).can():
            raise InvalidPermissionError(
                permission=self.permission(record)
            )
        return f(self, record, **kwargs)

    return inner


def has_valid_state(f):
    """Decorator to check the record is in a valid state for transition execution."""

    def inner(self, record, **kwargs):
        if record['state'] not in self.src:
            raise InvalidSourceStateError(source=record['state'], target=self.dest)
        return f(self, record, **kwargs)

    return inner


def has_required_params(trans):
    """Decorator to ensure that all required parameters has been passed to wrapped function."""
    def wrapper(f):
        def inner(self, *args, **kwargs):
            missing = [p for p in trans.REQUIRED_PARAMS if p not in kwargs]
            if missing:
                msg = "Required input parameters are missing '{}'".format(
                    missing
                )
                raise MissingRequiredParameterError(description=msg)

            return f(self, *args, **kwargs)
        return inner
    return wrapper


class Transition(object):
    """A transition specification class."""

    def __init__(
        self, src, dest, permission=None, required=None, **kwargs
    ):
        """Init transition object."""
        self.src = src
        self.dest = dest
        self.REQUIRED_PARAMS = required or []
        # default_perm = current_app.config[
        #     'OAREPO_FSM_DEFAULT_PERMISSION_FACTORY'
        # ]
        self.permission = permission  # or default_perm

    @has_valid_state
    @has_permission
    def execute(self, record, **kwargs):
        """Execute transition when conditions are met."""
        record['state'] = self.dest

    @has_permission
    def check_permission(self, record):
        """Check transition permission requirements."""
        return True


def transition(t: Transition):
    """Decorator that marks the wrapped function as a state transition.

    :params obj: :class:`~oarepo_fsm.mixins.Transition` a transition specification instance.
    :returns: A wrapper around a wrapped function, with added `_fsm` field containing the `Transition` spec.
    """
    def inner(f):
        @has_required_params(t)
        def wrapper(self, *args, **kwargs):
            t.execute(record=self, **kwargs)
            f(self, *args, **kwargs)

        wrapper._fsm = t
        return wrapper

    return inner
