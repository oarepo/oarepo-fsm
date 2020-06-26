from invenio_records import Record

from oarepo_fsm.decorators import transition, Transition
from oarepo_fsm.mixins import StatefulRecordMixin


class ExampleRecord(Record, StatefulRecordMixin):

    @transition(Transition(src='closed', dest='open'))
    def open(self):
        print('record opened')

    @transition(Transition(src='open', dest='closed'))
    def close(self):
        print('record closed')
