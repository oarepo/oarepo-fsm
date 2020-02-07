from flask import current_app
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound

from oarepo_fsm.proxies import current_oarepo_fsm
from oarepo_fsm.signals import before_fsmrecord_insert, after_fsmrecord_insert


def before_record_index_callback(sender, json=None, record=None, index=None,
                                 doc_type=None, arguments=None, **kwargs):
    # TODO: implement callback
    pass


def after_record_insert_callback(sender, *args, **kwargs):
    record = kwargs['record']
    FSMRecord.create(record=record, state=current_oarepo_fsm.get_initial_state(record))


class FSMRecord(object):
    """Define API for metadata creation and manipulation."""

    @classmethod
    def create(cls, record, state=None, **kwargs):
        """Create a new FSM record instance and store it in the database.

        #. Send a signal :data:`oarepo_fsm.signals.before_fsmrecord_insert`
           with the new fsm record as parameter.

        #. Add the new fsm record in the database.

        #. Send a signal :data:`invenio_records.signals.after_fsmrecord_insert`
           with the new created record as parameter.

        :Keyword Arguments:
        :param record_uuid: UUID of record to which the state should be attached.
        :param state: Initial state value
        :returns: A new :class:`FSMRecord` instance.
        """
        rec_cls = getattr(record, 'fsm_class', None)
        if not rec_cls:
            return None

        with db.session.begin_nested():
            fsmrec = rec_cls()
            fsmrec.record_uuid = record.id
            fsmrec.state = state

            before_fsmrecord_insert.send(
                current_app._get_current_object(),
                fsm_record=fsmrec,
                state=state
            )

            # record.validate(**kwargs)
            db.session.add(fsmrec)

        after_fsmrecord_insert.send(
            current_app._get_current_object(),
            fsm_record=fsmrec,
            state=state
        )
        return record

    @classmethod
    def get_fsm_record(cls, record):
        """Retrieve the FSM record for Invenio Record.

        Raise a database exception if the record does not exist.

        :param record_: Invenio Record instance.
        :returns: The :class:`FSMEnabledRecord` instance.
        """
        rec_cls = getattr(record, 'fsm_class', None)
        if not rec_cls:
            raise NoResultFound

        with db.session.no_autoflush:
            return rec_cls.query.filter_by(record_uuid=record.id).one()
