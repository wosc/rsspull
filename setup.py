"""Downloads RSS/Atom feeds and converts them to Maildir messages.
"""
from setuptools import setup, find_packages
import glob
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='ws.rsspull',
    version='2.0.dev0',

    install_requires=[
        'feedparser==4.1',
        'html2text<=3.0',
        'setuptools',
    ],

    entry_points={
        'console_scripts': [
            'rsspull = ws.rsspull.main:main'
        ],
    },

    author='Wolfgang Schnerring <wosc@wosc.de>',
    author_email='wosc@wosc.de',
    license='ZPL 2.1',
    url='https://bitbucket.org/wosc/ws.rsspull/',

    description=__doc__.strip(),
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
        'README.txt',
        'CHANGES.txt',
    )),

    namespace_packages=['ws'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    data_files=[('', glob.glob(project_path('*.txt')))],
    zip_safe=False,
)
