from flask_principal import RoleNeed
from invenio_access import Permission
from invenio_records import Record

from oarepo_fsm.decorators import Transition, transition
from oarepo_fsm.mixins import FSMMixin


def editor_permission(record):
    return Permission(RoleNeed('editor'))


def admin_permission(record):
    return Permission(RoleNeed('admin'))


class ExampleRecord(FSMMixin, Record):

    @transition(Transition(src=['closed'], dest='open', required=['id']))
    def open(self, **kwargs):
        print('record {} opened'.format(kwargs.get('id')))

    @transition(Transition(src=['open'], dest='closed', required=['id']))
    def close(self, **kwargs):
        print('record {} closed'.format(kwargs.get('id')))

    @transition(Transition(src=['open', 'archived'], dest='published', permissions=[editor_permission]))
    def publish(self, **kwargs):
        print('record published')

    @transition(Transition(src=['closed', 'published'], dest='archived', permissions=[admin_permission]))
    def archive(self, **kwargs):
        print('record archived')
