import uuid

from invenio_db import db
from invenio_records import Record

from oarepo_fsm.decorators import transition
from oarepo_fsm.mixins import StatefulRecordMixin


class ExampleRecord(Record, StatefulRecordMixin):
    pass


class ExampleFSM(db.Model):
    """Example FSM enabled record."""
    __tablename__ = 'examplefsm'

    record_uuid = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )

    @transition(source='closed', target='opened')
    def open(self, instance, value):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """
        pass

    @transition(source='opened', target='closed')
    def close(self, instance, value):
        pass
