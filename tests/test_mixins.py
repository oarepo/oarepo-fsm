# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import uuid

import pytest
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from examples import ExampleFSM

engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
SessionGen = sessionmaker(bind=engine)
Base = declarative_base()


def pytest_sessionstart():
    Base.metadata.create_all(engine)


@pytest.fixture(scope='function')
def session():
    Base.metadata.create_all(engine)  # Creates any dynamically imported tables
    return SessionGen()


@pytest.fixture
def model(db):
    # class ExampleFSM(db.Model):
    #     """Example FSM enabled record."""
    #     def __init__(self):
    #         self.state = 'closed'
    #         super(ExampleFSM, self).__init__()
    #
    #     record_uuid = db.Column(
    #         UUIDType,
    #         primary_key=True,
    #         default=uuid.uuid4,
    #     )
    #     state = db.Column(FSMField, default='closed', nullable=False)
    #
    #     @transition(source='closed', target='opened')
    #     def open(self, instance, value):
    #         """
    #         This function may contain side-effects,
    #         like updating caches, notifying users, etc.
    #         The return value will be discarded.
    #         """
    #         pass
    #
    #     @transition(source='opened', target='closed')
    #     def close(self, instance, value):
    #         pass

    return ExampleFSM()


def test_model_fsm(model, db):
    assert model.state == 'closed'
    assert not model.close.can_proceed()
    assert model.open.can_proceed()
    model.open.set(None, None)
    assert model.state == 'opened'
