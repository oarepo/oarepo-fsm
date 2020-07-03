#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""
import inspect

from jsonpatch import apply_patch

from oarepo_fsm.errors import DirectStateModificationError, \
    InvalidPermissionError


class StatefulRecordMixin(object):
    """
    Enhances Record model with FSM managed states.

    A mixin for Record class that makes sure state field could not be modified through a REST API updates.
    Note that this mixin is not enough, always use oarepo_fsm.marshmallow.StatePreservingMixin
    as well. The reason is that Invenio does not inject custom Record implementation for PUT, PATCH and DELETE
    operations.
    """

    def clear(self):
        """Preserves the state even if the record is cleared and all metadata wiped out."""
        state = self.get('state')
        super().clear()
        if state:
            self['state'] = state

    def patch(self, patch):
        """Patch record metadata.

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        self_data = dict(self)
        patched_data = apply_patch(dict(self), patch)

        if patched_data['state'] != self_data['state']:
            raise DirectStateModificationError()

        return self.__class__(patched_data, model=self.model)

    def update(self, e=None, **f):
        """Dictionary update."""
        self._check_schema(e or f)
        return super().update(e, **f)

    @classmethod
    def actions(cls):
        """All transition actions defined on a record model.

        :params cls:
        :returns: A dict of all actions defined on a record model.
        """
        if not getattr(cls, '_actions', False):
            cls._actions = {}
            funcs = inspect.getmembers(cls, predicate=inspect.isfunction)

            for act, fn in funcs:
                if getattr(fn, '_fsm', False):
                    cls._actions[act] = fn

        return cls._actions

    @classmethod
    def transitions(cls):
        """All transitions defined on a record model.

        :params cls:
        :returns: A dict of all transition specs defined on a record model.
        """
        return {act: getattr(fn, '_fsm') for act, fn in cls.actions().items()}

    @classmethod
    def user_actions(cls):
        """Actions that can be triggered by a current_user.

        :params cls:
        :returns: A dict of all actions that can be triggered by a current user.
        """
        ut = {}
        all_actions = cls.actions()

        for act, trans in cls.transitions().items():
            try:
                if trans.check_permission(None):
                    ut[act] = all_actions[act]
            except (InvalidPermissionError, KeyError):
                continue
        return ut
