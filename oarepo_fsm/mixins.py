#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""
import inspect

from oarepo_fsm.errors import DirectStateModificationError, \
    InvalidPermissionError


class FSMMixin(object):
    """
    Enhances Record model with FSM managed states.

    A mixin for Record class that makes sure state field could not be modified through a REST API updates.
    Note that this mixin is not enough, always use oarepo_fsm.marshmallow.StatePreservingMixin
    as well. The reason is that Invenio does not inject custom Record implementation for PUT, PATCH and DELETE
    operations.
    """

    STATE_FIELD = 'state'
    "State field name."

    _STATE_FIELD_PARSED = None
    "Parsed state field name"

    @classmethod
    def _deep_get_state(cls, data, state_field=None):
        """Internal method for getting state from nested field."""
        if not state_field:
            if not cls._STATE_FIELD_PARSED:
                cls._STATE_FIELD_PARSED = cls.STATE_FIELD.split('.')
            state_field = cls._STATE_FIELD_PARSED

        for s in state_field:
            if data:
                data = data.get(s)
        return data

    @classmethod
    def _deep_set_state(cls, data, state, state_field=None):
        """Internal method for getting state to nested field."""
        if not state_field:
            if not cls._STATE_FIELD_PARSED:
                cls._STATE_FIELD_PARSED = cls.STATE_FIELD.split('.')
            state_field = cls._STATE_FIELD_PARSED

        for s in state_field[:-1]:
            if s not in data:
                data[s] = {}
            data = data[s]
        data[state_field[-1]] = state
        return data

    def clear(self):
        """Preserves the state even if the record is cleared and all metadata wiped out."""
        state = self._deep_get_state(self)
        super().clear()
        if state:
            self._deep_set_state(self, state)

    def patch(self, patch):
        """Patch record metadata.

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        self_data = dict(self)
        record = super().patch(patch)
        patched_data = dict(record)

        if self._deep_get_state(patched_data) != self._deep_get_state(self_data):
            raise DirectStateModificationError()

        return record

    def update(self, e=None, **f):
        """Dictionary update."""
        return super().update(e, **f)

    @classmethod
    def all_transitions(cls):
        """All transition transitions defined on a record model.

        :params cls:
        :returns: A dict of all transitions defined on a record model.
        """
        if not getattr(cls, '_transitions', False):
            cls._transitions = {}

            # use dict directly and not inspect.getmembers as __dict__ seems to be sorted
            # by definition order and getmembers alphabetically. Definition order is better
            # because it enables to return the transitions in "logical" order.
            for pc in cls.mro():
                for act, fn in pc.__dict__.items():
                    if not inspect.isfunction(fn):
                        continue
                    if getattr(fn, '_fsm', False) and act not in cls._transitions.keys():
                        cls._transitions[act] = fn._fsm

        return cls._transitions

    def available_transitions(self):
        """Return all transitions that are allowed by record state."""
        return {k: v for k, v in self.all_transitions().items() if v.enabled_for_record(self)}

    @classmethod
    def all_user_transitions(cls):
        """Return all transitions allowed to be performed by current user."""
        ut = {}

        for k, trans in cls.all_transitions().items():
            try:
                if trans.has_permissions(None):
                    ut[k] = trans
            except (InvalidPermissionError, KeyError):
                continue
        return ut

    def available_user_transitions(self):
        """Return all transitions user can perform on this record at this time."""
        ut = {}

        for k, trans in self.available_transitions().items():
            try:
                if trans.has_permissions(self):
                    ut[k] = trans
            except (InvalidPermissionError, KeyError):
                continue
        return ut
