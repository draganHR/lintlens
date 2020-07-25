#!/usr/bin/env python
from codecs import open
import pkg_resources
from setuptools import setup, find_packages

import lintlens


packages = find_packages(include=('lintlens*',), exclude=('*.tests',))


with open('requirements/base.txt') as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


with open('requirements/tests.txt') as requirements_txt:
    tests_extras = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]


with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='lintlens',
    version=lintlens.__version__,
    description='Filters lint report and keep only defects on changed lines',
    long_description=readme,
    author='Dragan Bosnjak',
    url='https://github.com/draganHR/lintlens',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ),
    install_requires=install_requires,
    extras_require={
        'tests': tests_extras,
    },

    entry_points={
        'console_scripts': [
            'lintlens = lintlens.cli:main',
        ]
    },
    test_suite='tests'
)
