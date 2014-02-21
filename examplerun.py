from ws.rsspull.main import rsspull
import os
import pkg_resources
import shutil


confdir = 'work'
if not os.path.exists(confdir):
    os.mkdir(confdir)
maildir = os.path.join(confdir, 'Maildir')
if not os.path.exists(maildir):
    os.mkdir(maildir)
shutil.copy(pkg_resources.resource_filename(
    'ws.rsspull.tests', 'fixture/feeds.opml'), confdir)
shutil.copy(pkg_resources.resource_filename(
    'ws.rsspull.tests', 'fixture/config'), confdir)
rsspull(confdir)
