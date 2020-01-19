#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from urllib.parse import urlsplit, urlunparse

from flask import current_app
from invenio_indexer.utils import schema_to_index
from invenio_jsonschemas import current_jsonschemas
from jsonref import JsonRef


def get_search_index(json_schemas, url_prefix):
    """Return search indices from json schemas"""
    indices = [schema_to_index(x)[0] for x in json_schemas]
    indices = [x for x in indices if x]
    if len(indices) == 1:
        return indices[0]
    else:
        raise Exception(
            'Add "fsm_search_index" or "json_schemas" to '
            'OAREPO_FSM_ENABLED_RECORDS_REST_ENDPOINTS["%s"]' % url_prefix)


def internal_invenio_loader(relative_schema, *args, **kwargs):
    parts = urlsplit(relative_schema)
    if not parts.netloc:
        relative_schema = urlunparse((current_app.config['JSONSCHEMAS_URL_SCHEME'],
                                      current_app.config['JSONSCHEMAS_HOST'],
                                      relative_schema, None, None, None))
    path = current_jsonschemas.url_to_path(relative_schema)
    return current_jsonschemas.get_schema(path)


def get_schema(self, schema_path):
    schema_data = current_jsonschemas.get_schema(
        schema_path, with_refs=False, resolved=False)
    schema_data = JsonRef.replace_refs(
        schema_data,
        base_uri=current_jsonschemas.path_to_url(schema_path),
        loader=internal_invenio_loader
    )
    return current_jsonschemas.resolver_cls(schema_data)
