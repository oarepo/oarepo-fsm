#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from flask import current_app

from oarepo_fsm.errors import InvalidPermissionError


def transition(definition):
    def inner(f):
        def wrapper(self, *args, **kwargs):
            f(*args, **kwargs)
        wrapper._fsm = definition
        return wrapper
    return inner


def has_permission(f):
    """Decorator to check the transition should be manually triggered."""
    def inner(self, record, **kwargs):
        if self.permission_factory and not self.permission_factory(record).can():
            raise InvalidPermissionError(
                permission=self.permission_factory(record)
            )
        return f(self, record, **kwargs)
    return inner


class TransitionDefinition(object):
    """A transition specification."""

    def __init__(
        self, src, dest, permission_factory=None, **kwargs
    ):
        """Init transition object."""
        self.src = src
        self.dest = dest
        self.initial_state = None
        default_perm = current_app.config[
            "OAREPO_FSM_DEFAULT_PERMISSION_FACTORY"
        ]
        self.permission_factory = permission_factory or default_perm
        self.validate_transition_states()

    @has_permission
    def execute(self, loan, **kwargs):
        """Execute before actions, transition and after actions."""
        self._date_fields2datetime(kwargs)
        loan.date_fields2datetime()

        self.before(loan, **kwargs)
        loan["state"] = self.dest
        self.after(loan)
