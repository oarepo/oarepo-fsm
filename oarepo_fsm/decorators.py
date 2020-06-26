#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from flask import current_app

from oarepo_fsm.errors import InvalidPermissionError, InvalidSourceStateError


def has_permission(f):
    """Decorator to check the transition should be manually triggered."""
    def inner(self, record, **kwargs):
        if self.permission_factory and not self.permission_factory(record).can():
            raise InvalidPermissionError(
                permission=self.permission_factory(record)
            )
        return f(self, record, **kwargs)
    return inner


class Transition(object):
    """A transition class."""

    def __init__(
        self, src, dest, permission_factory=None, **kwargs
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
        # self.permission_factory = permission_factory or default_perm

    def validate_source_state(self, record):
        """Ensure that source and destination states are valid."""
        if record['state'] != self.src:
            raise InvalidSourceStateError(source=self.src, target=self.dest)

    @has_permission
    def execute(self, record, **kwargs):
        """Execute transition when conditions are met."""
        self.validate_source_state(record)

        record['state'] = self.dest


def transition(obj: Transition):
    def inner(f):
        def wrapper(self, *args, **kwargs):
            obj.execute(self, *args, **kwargs)
            f(*args, **kwargs)
        wrapper._fsm = obj
        return wrapper
    return inner
