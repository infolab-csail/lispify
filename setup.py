from setuptools import setup

setup(
    name='lispify',
    version='1.0.0',
    description=('Lispify converts Python objects into Lisp-like '
                 'encoded strings that are interpretable in Common Lisp.'),
    url='https://github.com/infolab-csail/lispify.git',
    packages=[
        'lispify',
        'tests',
    ],
    install_requires=[
        'future',
    ],
    tests_require=[
        'unittest2',
        'nose>=1.0',
    ],
    test_suite='nose.collector',
)
