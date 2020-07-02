#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

from oarepo_fsm.errors import InvalidPermissionError, InvalidSourceStateError


def has_permission(f):
    """Decorator to check the transition should be manually triggered."""

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


class Transition(object):
    """A transition specification class."""

    def __init__(
        self, src, dest, permission=None, **kwargs
    ):
        """Init transition object."""
        self.src = src
        self.dest = dest
        # self.initial_state = current_app.config.get(
        #     'OAREPO_FSM_INITIAL_STATE', None
        # )
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
        return True


def transition(obj: Transition):
    def inner(f):
        def wrapper(self, *args, **kwargs):
            obj.execute(record=self, **kwargs)
            f(self, *args, **kwargs)

        wrapper._fsm = obj
        return wrapper

    return inner
