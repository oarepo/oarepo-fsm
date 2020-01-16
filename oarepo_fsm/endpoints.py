#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""
#
# class PublishedLinksFactory(LinksFactory):
#     def __call__(self, pid, record=None, **kwargs):
#         resp = self.links_factory(pid, record=record, **kwargs)
#         other_end = self.get_other_end_link(pid)
#         if other_end and self.edit_permission_factory(record=record).can():
#             resp['draft'] = other_end
#
#         if record and self.unpublish_permission_factory(record=record).can():
#             resp['unpublish'] = url_for(
#                 'invenio_records_draft.unpublish_{0}'.format(self.endpoint_name),
#                 pid_value=pid.pid_value,
#                 _external=True
#             )
#
#         if record and self.edit_permission_factory(record=record).can():
#             resp['edit'] = url_for(
#                 'invenio_records_draft.edit_{0}'.format(self.endpoint_name),
#                 pid_value=pid.pid_value,
#                 _external=True
#             )
#
#         resp.update(self.get_extra_url_rules(pid))
#
#         return resp
