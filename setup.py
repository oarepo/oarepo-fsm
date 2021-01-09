# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# oarepo-fsm is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo FSM library for record state transitions"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()
OAREPO_VERSION = os.environ.get('OAREPO_VERSION', '3.3.0')

install_requires = [
    'wrapt>=1.11.2'
]

deploy_requires = [
    'oarepo[deploy]~={version}'.format(version=OAREPO_VERSION),
]

tests_require = [
    'oarepo[tests]~={version}'.format(version=OAREPO_VERSION),
]

extras_require = {
    'tests': tests_require,
    'tests-es7': {
        'oarepo[tests-es7]~={version}'.format(version=OAREPO_VERSION),
    },
    'devel': tests_require,
    'deploy': deploy_requires,
}

setup_requires = [
    'pytest-runner>=2.7',
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('oarepo_fsm', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='oarepo-fsm',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='fsm fsm-library oarepo records state-management',
    license='MIT',
    author='CESNET',
    author_email='bauer@cesnet.cz',
    url='https://github.com/oarepo/oarepo-fsm',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_db.models': [
            'oarepo_fsm = examples.models',
        ],
        'invenio_base.apps': [
            'oarepo_fsm = oarepo_fsm.ext:OARepoFSM',
        ],
        'invenio_base.api_apps': [
            'oarepo_fsm = oarepo_fsm.ext:OARepoFSM',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
