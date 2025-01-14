import os
from setuptools import setup
import nrt_logging

PATH = os.path.dirname(__file__)

with open(os.path.join(PATH, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

with open(os.path.join(PATH, 'README.md')) as f:
    readme = f.read()

setup(
    name='nrt-logging',
    version=nrt_logging.__version__,
    author='Eyal Tuzon',
    author_email='eyal.tuzon.dev@gmail.com',
    description='Hierarchical logging in yaml format',
    keywords='python python3 python-3 logging logger log loggers'
             ' logging-library logging-framework hierarchical hierarchy'
             ' yaml nrt nrt-logging',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/etuzon/python-nrt-logging',
    packages=['nrt_logging'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[requirements],
    data_files=[('', ['requirements.txt'])],
)
