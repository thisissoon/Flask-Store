# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Flask-Store
-----------

Flask-Store is a Flask Extenstion which provides easy Django-Storages style
file handling to various storage backends.
"""

# Temporary patch for issue reported here:
# https://groups.google.com/forum/#!topic/nose-users/fnJ-kAUbYHQ
import multiprocessing  # noqa
import os
import sys
import warnings

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def read_requirements(filename):
    """ Read requirements file and process them into a list
    for usage in the setup function.

    Arguments
    ---------
    filename : str
        Path to the file to read line by line

    Returns
    --------
    list
        list of requirements::

            ['package==1.0', 'thing>=9.0']
    """

    requirements = []

    try:
        with open(filename, 'rb') as f:
            for line in f.readlines():
                line = line.strip()
                if not line or line.startswith('#') or line == '':
                    continue
                requirements.append(line)
    except IOError:
        warnings.warn('{0} was not found'.format(filename))

    return requirements

# Get current working directory

try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

# Change to current working directory

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

# Requirements

INSTALL_REQUIREMENTS = read_requirements('REQS.txt')
TESTING_REQUIREMENTS = read_requirements('REQS.TESTING.txt')
DEVELOP_REQUIREMENTS = read_requirements('REQS.DEVELOP.txt') \
    + TESTING_REQUIREMENTS

# Include the Change Log on PyPi

long_description = open('README.rst').read()
changelog = open('CHANGELOG.rst').read()
long_description += '\n' + changelog

# Setup

setup(
    name='Flask-Store',
    version=open('VERSION').read().strip(),
    author='SOON_',
    author_email='dorks@thisissoon.com',
    maintainer='Chris Reeves',
    maintainer_email='hello@chris.reeves.io',
    url='http://flask-store.soon.build',
    description='Provides Django-Storages like file storage backends for '
                'Flask Applications.',
    long_description=long_description,
    packages=find_packages(
        exclude=[
            'tests'
        ]),
    include_package_data=True,
    zip_safe=False,
    # Dependencies
    install_requires=INSTALL_REQUIREMENTS,
    extras_require={
        'develop': DEVELOP_REQUIREMENTS
    },
    # Testing
    tests_require=TESTING_REQUIREMENTS,
    cmdclass={
        'test': PyTest
    },
    # Dependencies not hosted on PyPi
    dependency_links=[],
    # Classifiers for Package Indexing
    # Entry points, for example Flask-Script
    entry_points={},
    # Meta
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],
    license='MIT',
    keywords=['Flask', 'Files', 'Storage'])
