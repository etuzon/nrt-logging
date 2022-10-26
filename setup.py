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
    keywords='logging logger log hierarchical hierarchy yaml',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/etuzon/Python-NRT-Logging',
    packages=['nrt_logging'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
    install_requires=[requirements],
    data_files=[('', ['requirements.txt'])],
)
