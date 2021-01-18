from flask import make_response
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

    @transition(src=['closed'], dest='open', required=['id'])
    def open(self, **kwargs):
        print('record {} opened'.format(kwargs.get('id')))

    @transition(src=['open'], dest='closed', required=['id'])
    def close(self, **kwargs):
        print('record {} closed'.format(kwargs.get('id')))

    @transition(src=['open', 'archived'], dest='published', permissions=[editor_permission])
    def publish(self, **kwargs):
        print('record published')

    @transition(src=['closed', 'published'], dest='archived', permissions=[admin_permission])
    def archive(self, **kwargs):
        print('record archived')

    @transition(src=['published', 'closed'], dest='deleted', commit_record=False)
    def delete(self, **kwargs):
        print('deleting record')
        return make_response(
            {'status': 'deleted'},
            202
        )
