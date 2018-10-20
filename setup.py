#!/usr/bin/env python
from codecs import open
from setuptools import setup, find_packages

import lintlens


packages = find_packages(exclude=('tests',))


requires = [
    'six>=1.9.0',
]

tests_require = [
    'pytest>=3.7.0',
]


with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='lintlens',
    version=lintlens.__version__,
    description='...',
    long_description=readme,
    author='Dragan Bosnjak',
    url='https://github.com/draganHR',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    install_requires=requires,
    extras_require={
        'tests': tests_require,
    },

    entry_points={
        'console_scripts': [
            'lintlens = lintlens.cli:main',
        ]
    },
    test_suite='tests'
)
