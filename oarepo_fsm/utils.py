#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from urllib.parse import urlsplit, urlunparse

from flask import current_app
from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.utils import obj_or_import_string
from jsonref import JsonRef


def internal_invenio_loader(relative_schema, *args, **kwargs):
    parts = urlsplit(relative_schema)
    if not parts.netloc:
        relative_schema = urlunparse((current_app.config['JSONSCHEMAS_URL_SCHEME'],
                                      current_app.config['JSONSCHEMAS_HOST'],
                                      relative_schema, None, None, None))
    path = current_jsonschemas.url_to_path(relative_schema)
    return current_jsonschemas.get_schema(path)


def get_schema(schema_path):
    schema_data = current_jsonschemas.get_schema(
        schema_path, with_refs=False, resolved=False)
    schema_data = JsonRef.replace_refs(
        schema_data,
        base_uri=current_jsonschemas.path_to_url(schema_path),
        loader=internal_invenio_loader
    )
    return current_jsonschemas.resolver_cls(schema_data)


def convert_relative_schema_to_absolute(x):
    """Convert relative record schema to absolute if needed."""
    if x.startswith('http://') or x.startswith('https://'):
        return x
    return current_jsonschemas.path_to_url(x)


def pid_getter(kw):
    if 'pid_getter' in kw:
        return kw.pop('pid_getter')
    record_class = obj_or_import_string(kw['record_class'])
    record_module_name = record_class.__module__
    record_class_name = record_class.__name__
    pid_type = kw.get('pid_type', 'recid')
    pid = f'pid({pid_type},record_class="{record_module_name}:{record_class_name}")'
    return f'<{pid}:pid_value>'
