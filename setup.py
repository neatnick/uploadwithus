try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import uploadwithus

setup(
    name='uploadwithus',
    version=uploadwithus.__version__,
    description='CLI to facilitate keeping sendwithus templates and snippets code up to date with an emails repository.',
    long_description=uploadwithus.__doc__,
    author=uploadwithus.__author__,
    author_email='nbalboni2@gmail.com',
    url='https://github.com/SwankSwashbucklers/uploadwithus',
    install_requires=[
        'PyYAML >= 3.11',
        'sendwithus >= 1.8.0',
        'cached-property >= 1.3.0',
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
