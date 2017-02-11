try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='uploadwithus',
    version='0.2.5',
    description='CLI to facilitate keeping sendwithus templates and snippets code up to date with an emails repository.',
    long_description="""\
Uploadwithus is a command line tool to facilitate keeping sendwithus templates
and snippets code up to date with an emails repository.  The tool allows you to
maintain your email templates and snippets under a version control system, and
also allows separation of testing and production emails.  For more in depth
information on its usage and features, check out the README.

Copyright (c) 2017, Nick Balboni.
License: MIT (see LICENSE for details)
    """,
    author='Nick Balboni',
    author_email='nbalboni2@gmail.com',
    url='https://github.com/SwankSwashbucklers/uploadwithus',
    install_requires=[
        'PyYAML >= 3.11',
        'sendwithus >= 1.8.0',
        'cached-property >= 1.3.0',
        'future >= 0.16.0',
    ],
    py_modules=['uploadwithus'],
    scripts=['uploadwithus.py'],
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'uploadwithus = uploadwithus:main',
        ],
    },
)
