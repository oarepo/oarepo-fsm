from flask_principal import RoleNeed
from invenio_access import Permission
from invenio_records import Record

from oarepo_fsm.decorators import transition, Transition
from oarepo_fsm.mixins import StatefulRecordMixin


def editor_permission(record):
    return Permission(RoleNeed('editor'))


def admin_permission(record):
    return Permission(RoleNeed('admin'))


class ExampleRecord(Record, StatefulRecordMixin):

    @transition(Transition(src=['closed'], dest='open'))
    def open(self):
        print('record opened')

    @transition(Transition(src=['open'], dest='closed'))
    def close(self):
        print('record closed')

    @transition(Transition(src=['open', 'archived'], dest='published', permission=editor_permission))
    def publish(self):
        print('record published')

    @transition(Transition(src=['closed', 'published'], dest='archived', permission=admin_permission))
    def archive(self):
        print('record archived')
