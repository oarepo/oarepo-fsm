#
# Copyright (C) 2020 CESNET.
#
# examples is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""


def before_record_index_callback(sender, json=None, record=None, index=None,
                                 doc_type=None, arguments=None, **kwargs):
    # TODO: implement callback
    pass


def after_record_insert_callback(sender, *args, **kwargs):
    record = kwargs['record']
    # TODO: implement callback
