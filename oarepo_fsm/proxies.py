#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions."""

from flask import current_app
from werkzeug.local import LocalProxy

current_oarepo_fsm = LocalProxy(
    lambda: current_app.extensions['oarepo-fsm'])
"""Helper proxy to access fsm state object."""
