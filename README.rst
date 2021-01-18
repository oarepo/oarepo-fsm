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

Check that correct record_class is being used on the RECORDS_REST_ENDPOINT's item_route ::

    item_route='/records/<pid(recid,record_class="yourapp.models:RecordModelFSM"):pid_value>',

To automatically add a link to the FSM endpoint to your record links, use the following ``links_factory_imp`` in
your **RECORDS_REST_ENDPOINTS** config ::

    links_factory_imp='oarepo_fsm.links:record_fsm_links_factory',

If you wish to activate FSM on a certain Record enpoints only, put in your config ::

    OAREPO_FSM_ENABLED_REST_ENDPOINTS = ['recid']

Where **recid** is the prefix key into your **RECORDS_REST_ENDPOINTS** configuration.
This library activates FSM on all endpoints using `record_class` inherited from `FSMMixin` otherwise.

Usage
-----

In order to use this library, you need to define a Record
model in your app, that inherits from a **FSMMixin** column ::

    from invenio_records import Record
    from oarepo_fsm.mixins import FSMMixin

    class RecordModelFSM(FSMMixin, Record):
    ...

To define FSM transitions on this class, create methods decorated with **@transition(..)** e.g. ::

    @transition(
        src=['open', 'archived'],
        dest='published',
        required=['id'],
        permissions=[editor_permission],
        commit_record=True)
    def publish(self, **kwargs):
        print('record published')

Where decorator parameters mean:

  - **src**: record must be in one of the source states before transition could happen
  - **dest**: target state of the transition
  - **required**: a list of required ``**kwargs`` that must be passed to the ``@transition`` decorated function
  - **permissions**: currently logged user must have at least one of the permissions to execute the transition
  - **commit_record**: should the changes made in a record be commited after the function returns?

A transition-decorated function can optionally return a custom flask Response or a JSON-serializable
dict to be provided to user in a JSON response.

REST API Usage
--------------

To get current record state and possible transitions (only transitions that you have permission to invoke will be returned) ::

    GET <record_rest_item_endpoint>
    >>>
    {
        metadata: {
            state: <current state of the record>
            ... other record metadata
        }
        links: {
            self: ...,
            "transitions": {
                <fsm_transition1_name>: <transition_url>,
                <fsm_transition2_name>: <transition_url>,
            },
            ...
        }
    }

To invoke a specific transition transition, do ::

    POST <record_rest_endpoint>/<fsm_transition_name>


Further documentation is available on
https://oarepo-fsm.readthedocs.io/


Permission factories
--------------------

Sometimes access to records should be governed by the state of the record. For example,
if the record is in ``state=editing``, any editor can make changes. If it is ``state=approving``,
only the curator can modify the record.

On REST level, modification permissions are governed by permission factories ::

    from invenio_records_rest.utils import allow_all, deny_all
    RECORDS_REST_ENDPOINTS = dict(
        recid=dict(
           create_permission_factory_imp=deny_all,
           delete_permission_factory_imp=deny_all,
           update_permission_factory_imp=deny_all,
           read_permission_factory_imp=allow_all,
       )
    )

This library provides the following factories and helpers:

   * ``transition_required(*transitions)`` allows user if
     he is entitled to perform any of the transitions (
     method names) on the current record
   * ``states_required(*states, state_field="state"`` allows
     anyone if the record is in any of the states mentioned
   * ``require_all(*perms_or_factories)`` allows user only if all
     permissions allow. Use it with states_required as follows ::

        require_all(
            states_required('editing'),
            editing_user_permission_factory
        )

     where editing_user_permission_factory is a permission factory allowing only
     editing users.
   * ``require_any(*perms_or_factories)`` allows user if any of
     the permissions allow. Example ::

        require_any(
            require_all(
                states_required('editing'),
                editing_user_permission_factory
            ),
            require_all(
                states_required('editing', 'approving),
                curator_user_permission_factory
            ),
        )
