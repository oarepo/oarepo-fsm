..
    Copyright (C) 2020 CESNET.

    oarepo-fsm is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

============
 oarepo-fsm
============

.. image:: https://img.shields.io/travis/oarepo/oarepo-fsm.svg
        :target: https://travis-ci.org/oarepo/oarepo-fsm

.. image:: https://img.shields.io/coveralls/oarepo/oarepo-fsm.svg
        :target: https://coveralls.io/r/oarepo/oarepo-fsm

.. image:: https://img.shields.io/github/tag/oarepo/oarepo-fsm.svg
        :target: https://github.com/oarepo/oarepo-fsm/releases

.. image:: https://img.shields.io/pypi/dm/oarepo-fsm.svg
        :target: https://pypi.python.org/pypi/oarepo-fsm

.. image:: https://img.shields.io/github/license/oarepo/oarepo-fsm.svg
        :target: https://github.com/oarepo/oarepo-fsm/blob/master/LICENSE

OArepo FSM  library for record state transitions built on top of the https://pypi.org/project/sqlalchemy-fsm/ library.


Quickstart
----------

Run the following commands to bootstrap your environment ::

    git clone https://github.com/oarepo/oarepo-fsm
    cd oarepo-fsm
    pip install -e .[devel]


Configuration
-------------

To use this library, specify the FSM enabled Record enpoints in your config like this ::

    OAREPO_FSM_ENABLED_REST_ENDPOINTS = ['recid']

Where **recid** is the prefix key into your **RECORDS_REST_ENDPOINTS** configuration.

Check that correct record_class is being used on the RECORDS_REST_ENDPOINT's item_route ::

    item_route='/records/<pid(recid,record_class="yourapp.models:RecordModelFSM"):pid_value>',


Usage
-----

In order to use this library, you need to define a Record
model in your app, that inherits from a **FSMMixin** column ::

    from invenio_records import Record
    from oarepo_fsm.mixins import FSMMixin

    class RecordModelFSM(FSMMixin, Record):
    ...

To define FSM transitions on this class, create methods decorated with **@transition(..)** e.g. ::

    @transition(Transition(src=['open', 'archived'], dest='published', permission=editor_permission))
    def publish(self):
        print('record published')


REST API Usage
--------------

To get current record state and possible transitions (only actions that you have permission to invoke will be returned) ::

    GET <record_rest_endpoint>/fsm
    >>>
    {
        metadata: {
            state: <current state of the record>
        }
        links: {
            actions: {
                <action_name>: <action_url>,
                ...
        }
    }

To invoke a specific transition action, do ::

    POST <record_rest_endpoint>/fsm/<action_name>


Further documentation is available on
https://oarepo-fsm.readthedocs.io/
