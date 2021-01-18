#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from oarepo_fsm.errors import InvalidPermissionError, \
    InvalidSourceStateError, MissingRequiredParameterError


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
        self,
        src,
        dest,
        state='state',
        permissions=None,
        required=None,
        commit_record=True,
        **kwargs
    ):
        """Init transition object."""
        self.src = src
        self.dest = dest
        self.state = state
        self.REQUIRED_PARAMS = required or []
        self.permissions = permissions or []  # or default_perms
        self.function = None
        self.original_function = None
        self.commit_record = commit_record

    def enabled_for_record(self, record):
        """Return if this transition can be applied to the record."""
        return record.get(self.state, None) in self.src

    def check_valid_state(self, record):
        """Check if transition can be applied to the record; if not, raise exception."""
        if not self.enabled_for_record(record):
            raise InvalidSourceStateError(source=record.get(self.state, None), target=self.dest)

    def check_permissions(self, record):
        """Check if user has permission to this transition and record; if not, raise exception."""
        if not self.has_permissions(record=record):
            raise InvalidPermissionError(
                permissions=self.permissions
            )

    def has_permissions(self, record=None):
        """Return true if user has permission to this transition and record."""
        if not self.permissions:
            return True
        for p in self.permissions:
            if callable(p):
                p = p(record=record)
            if p.can():
                return True
        return False

    def execute(self, record, **kwargs):
        """Execute transition when conditions are met."""
        record[self.state] = self.dest


def transition(src,
               dest,
               state='state',
               permissions=None,
               required=None,
               commit_record=True,
               **kwargs):
    """Decorator that marks the wrapped function as a state transition.

    :params parameters for transition object, see documentation for details.
    :returns: A wrapper around a wrapped function, with added `_fsm` field containing the `Transition` spec.
    """
    if permissions is not None and not isinstance(permissions, (list, tuple)):
        permissions = [permissions]
    if required is not None and not isinstance(required, (list, tuple)):
        required = [required]
    if not isinstance(src, (list, tuple)):
        src = [src]

    t = Transition(
        src=src,
        dest=dest,
        state=state,
        permissions=permissions,
        required=required,
        commit_record=commit_record,
        **kwargs
    )

    def inner(f):
        @has_required_params(t)
        def wrapper(self, *args, **kwargs):
            record = self
            t.check_valid_state(record)
            t.check_permissions(record)
            t.execute(record=record, **kwargs)
            return f(self, *args, **kwargs)

        wrapper._fsm = t
        t.function = wrapper
        t.original_function = f
        return wrapper

    return inner
