import uuid

from invenio_db import db
from invenio_records import Record
from sqlalchemy_fsm import transition, FSMField
from sqlalchemy_utils import UUIDType


class ExampleRecord(Record):
    @property
    def fsm_class(self):
        return ExampleFSM


class ExampleFSM(db.Model):
    """Example FSM enabled record."""

    def __init__(self):
        self.state = 'closed'
        super(ExampleFSM, self).__init__()

    record_uuid = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    state = db.Column(FSMField, default='closed', nullable=False)

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
