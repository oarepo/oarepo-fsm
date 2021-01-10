#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""
import json

from flask_login import current_user
from invenio_rest.errors import RESTException


class FSMException(RESTException):
    """Base Exception for OArepo FSM module, inherit, don't raise."""

    code = 400

    @property
    def name(self):
        """The status name."""
        return type(self).__name__

    def get_body(self, environ=None):
        """Get the request body."""
        body = dict(
            status=self.code,
            message=self.get_description(environ),
            error_module="OArepo-FSM",
            error_class=self.name,
        )

        errors = self.get_errors()
        if self.errors:
            body["errors"] = errors

        if self.code and (self.code >= 500) and hasattr(g, "sentry_event_id"):
            body["error_id"] = str(g.sentry_event_id)

        return json.dumps(body)


class MissingRequiredParameterError(FSMException):
    """Exception raised when required parameter is missing."""


class DirectStateModificationError(FSMException):
    """Raised when a direct modification of record state is attempted."""

    code = 403

    def __init__(self, **kwargs):
        """Initialize exception."""
        self.description = (
            "Direct modification of state is not allowed."
        )
        super().__init__(**kwargs)


class TransitionNotAvailableError(FSMException):
    """Raised when the requested transition is not available to current user."""

    code = 404

    def __init__(self, transition=None, **kwargs):
        """Initialize exception."""
        self.description = (
            "Transition {} is not available on this record".format(transition)
        )
        super().__init__(**kwargs)


class InvalidSourceStateError(FSMException):
    """Raised when source state of the record is invalid for transition."""

    def __init__(self, source=None, target=None, **kwargs):
        """Initialize exception."""
        self.description = (
            "Transition from {} to {} is not allowed".format(source, target)
        )
        super().__init__(**kwargs)


class RecordNotStatefulError(FSMException):
    """Raised when record does not inherit FSMMixin."""

    def __init__(self, record_cls=None, **kwargs):
        """Initialize exception."""
        self.description = (
            "{} must be a subclass of oarepo_fsm.mixins.FSMMixin".format(record_cls)
        )
        super().__init__(**kwargs)


class InvalidPermissionError(FSMException):
    """Raised when permissions are not satisfied for transition."""

    code = 403

    def __init__(self, permissions=None, **kwargs):
        """Initialize exception."""
        self.description = (
            "This transition is not permitted "
            "for your user {}. Required: '{}'".format(current_user, permissions)
        )
        super().__init__(**kwargs)
