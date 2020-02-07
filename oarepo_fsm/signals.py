#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
from blinker import Namespace

_signals = Namespace()

before_fsmrecord_insert = _signals.signal('before-fsmrecord-insert')
after_fsmrecord_insert = _signals.signal('after-fsmrecord-insert')
