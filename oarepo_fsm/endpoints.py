#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
import re

from flask import url_for
from flask.helpers import locked_cached_property
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import Record
from invenio_records_rest.serializers import JSONSerializer, record_responsify, search_responsify
from invenio_records_rest.utils import allow_all, obj_or_import_string, deny_all

from oarepo_fsm.models import FSMRecord

DEFAULT_LINKS_FACTORY = 'invenio_records_rest.links.default_links_factory'


def create_fsm_endpoint(
    url_prefix,
    fsm_endpoint, record_endpoint,
    record_marshmallow, search_index, record_pid_type,
    transition_permission_factory, fsm_permission_factory,
    extra_urls=None,
    **kwargs
):
    fsm_kwargs = {}
    fsm_kwargs.setdefault('pid_type', 'recid')
    fsm_kwargs.setdefault('pid_minter', 'recid')
    fsm_kwargs.setdefault('pid_fetcher', 'recid')
    fsm_kwargs.setdefault('record_class', Record)
    # fsm_kwargs.setdefault('fsm_record_class', FSMRecord)

    fsm_kwargs.setdefault('default_endpoint_prefix', True)
    fsm_kwargs.setdefault('list_route', f'/{url_prefix}/')
    fsm_kwargs.setdefault('default_media_type', 'application/json')
    if not fsm_kwargs.get('item_route'):
        fsm_kwargs['item_route'] = f'{url_prefix}/{pid_getter(fsm_kwargs)}'

    fsm_kwargs.setdefault('search_index', search_index)
    fsm_read_permission_factory = \
        fsm_kwargs.pop('read_permission_factory', None)
    fsm_modify_permission_factory = \
        fsm_kwargs.pop('modify_permission_factory', None)

    fsm_kwargs.setdefault('read_permission_factory_imp',
                                fsm_read_permission_factory or allow_all)
    fsm_kwargs.setdefault('create_permission_factory_imp',
                                fsm_modify_permission_factory or deny_all)
    fsm_kwargs.setdefault('update_permission_factory_imp',
                                fsm_modify_permission_factory or allow_all)
    fsm_kwargs.setdefault('delete_permission_factory_imp',
                                fsm_modify_permission_factory or deny_all)
    fsm_kwargs.setdefault('list_permission_factory_imp',
                                allow_all)

    _set_record_serializers(fsm_kwargs, record_marshmallow, lambda x: x)
    _set_search_serializers(fsm_kwargs, record_marshmallow, lambda x: x)

    fsm_kwargs['links_factory_imp'] = \
        FSMLinksFactory(fsm_endpoint, record_pid_type, record_endpoint,
                        fsm_kwargs.get('links_factory_imp',
                                         DEFAULT_LINKS_FACTORY),
                        fsm_permission_factory,
                        transition_permission_factory)

    return fsm_kwargs


def pid_getter(kw):
    if 'pid_getter' in kw:
        return kw.pop('pid_getter')
    record_class = obj_or_import_string(kw['record_class'])
    record_module_name = record_class.__module__
    record_class_name = record_class.__name__
    pid_type = kw.get('pid_type', 'recid')
    pid = f'pid({pid_type},record_class="{record_module_name}:{record_class_name}")'
    return f'<{pid}:pid_value>'


def _set_record_serializers(kw, record_marshmallow, wrapper):
    if 'record_serializers' not in kw:
        kw['record_serializers'] = {}
    rs = kw['record_serializers']
    for mime, sc in kw.pop('serializer_classes', {
        'application/json': JSONSerializer
    }).items():
        if mime not in rs:
            serializer_class = obj_or_import_string(sc)
            serialized = serializer_class(wrapper(
                obj_or_import_string(record_marshmallow)), replace_refs=True)
            rs[mime] = record_responsify(serialized, mime)


def _set_search_serializers(kw, record_marshmallow, wrapper):
    if 'search_serializers' not in kw:
        kw['search_serializers'] = {}
    rs = kw['search_serializers']
    for mime, sc in kw.pop('search_serializer_classes', {
        'application/json': JSONSerializer
    }).items():
        if mime not in rs:
            serializer_class = obj_or_import_string(sc)
            serialized = serializer_class(wrapper(
                obj_or_import_string(record_marshmallow)), replace_refs=True)
            rs[mime] = search_responsify(serialized, mime)


class LinksFactory:
    def __init__(self, endpoint_name, other_end_pid_type,
                 other_end_endpoint_name, links_factory,
                 fsm_permission_factory,
                 transition_permission_factory):
        self.endpoint_name = endpoint_name
        self._links_factory = links_factory
        self.other_end_pid_type = other_end_pid_type
        self.other_end_endpoint_name = other_end_endpoint_name
        self.fsm_permission_factory = fsm_permission_factory
        self.transition_permission_factory = transition_permission_factory

    @locked_cached_property
    def links_factory(self):
        return obj_or_import_string(self._links_factory)

    def get_other_end_link(self, pid):
        try:
            # check if other side pid exists
            other_side_pid = PersistentIdentifier.get(self.other_end_pid_type, pid.pid_value)
            if other_side_pid.status != PIDStatus.DELETED:
                endpoint = 'invenio_records_rest.{0}_item'.format(self.other_end_endpoint_name)
                return url_for(endpoint, pid_value=pid.pid_value, _external=True)
        except PIDDoesNotExistError:
            pass
        return None


class FSMLinksFactory(LinksFactory):
    def __call__(self, pid, record=None, **kwargs):
        resp = self.links_factory(pid, record=record, **kwargs)
        other_end = self.get_other_end_link(pid)
        if other_end:
            resp['state'] = other_end

        if record and self.fsm_permission_factory(record=record).can():
            resp['state'] = url_for(
                'oarepo_fsm.state_{0}'.format(self.endpoint_name),
                pid_value=pid.pid_value, _external=True
            )
        return resp
