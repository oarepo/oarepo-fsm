#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
import inspect

from jsonpatch import apply_patch


class StatefulRecordMixin(object):
    """
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
        data = apply_patch(dict(self), patch)
        return self.__class__(data, model=self.model)

    def update(self, e=None, **f):
        """Dictionary update."""
        self._check_schema(e or f)
        return super().update(e, **f)

    @classmethod
    def get_states(cls):
        if not getattr(cls, '_states'):
            funcs = inspect.getmembers(cls, predicate=inspect.isfunction)
            cls._states = [fn for fn in funcs if getattr(fn, '_fsm')]
        else:
            return cls._states

    def get_transitions(self):
        pass

    def get_user_transitions(self):
        pass
