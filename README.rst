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

Usage
-----

In order to use this library, you need to define a Record
model in your app, that inherits from a **StatefulRecordMixin** column ::

    from invenio_records import Record
    from oarepo_fsm.mixins import StatefulRecordMixin

    class RecordModelFSM(StatefulRecordMixin, Record):
    ...

To define FSM transitions on this class, create methods decorated with **@transition(...)**, e.g.:

    @transition(Transition(src=['open', 'archived'], dest='published', permission=editor_permission))
    def publish(self):
        print('record published')


REST API Usage
--------------

To get current record state and possible transitions (transitions wil be filtered with a permission factory/guards) ::

    GET <record_rest_endpoint>/fsm
    >>>
    {
        state: <state representation as in details>,
        transitions: [<transition representation as in details>]
    }

Transition record to a new state ::

    POST <record_rest_endpoint>/fsm
    {
      transition: <transition code>
    }




Details
-------

Indexer
........

This library provides a **before_record_index** hook, that looks for
the indexed record's current state in the FSM model configured by **OAREPO_FSM**.
When it founds one, it adds the following field before indexing the record ::

    _invenioRecordState: {
        state: <code>,
       transitions:
         {
          next.code: <next.docstring>,
         },
    }

Signals
.......

This library listens to the **after_record_insert** signal and automatically
inserts corresponding entries to the FSM model configured by **OAREPO_FSM** for
records with matching schema.

Further documentation is available on
https://oarepo-fsm.readthedocs.io/
