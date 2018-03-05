from ws.rsspull.feed import Feed
import logging
import os
import os.path
import threading
import ws.rsspull.util

try:
    from ConfigParser import ConfigParser
    from Queue import Queue, Empty
except ImportError:
    from configparser import ConfigParser
    from queue import Queue, Empty


class Worker(threading.Thread):

    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            try:
                feed = self.queue.get_nowait()
                feed.sendNewEntries()
            except Empty:
                break


def rsspull(confdir):
    confdir = os.path.expanduser(confdir)
    config = ConfigParser()
    config.read(os.path.join(confdir, 'config'))
    Feed.workdir = os.path.join(confdir, 'cache')
    Feed.maildir = os.path.expanduser(config.get('global', 'maildir'))

    ws.rsspull.util.setupLogging(os.path.expanduser(
        config.get('global', 'logfile')))
    log = logging.getLogger(__name__)
    log.info('Reading feed configuration from %s' % confdir)
    feeds = Feed.parseOPML(os.path.join(confdir, 'feeds.opml'))

    worker_count = config.getint('global', 'workers')
    if worker_count > 1:
        rsspull_parallel(feeds, worker_count)
    else:
        rsspull_serial(feeds)


def rsspull_parallel(feeds, worker_count):
    queue = Queue(-1)
    for feed in feeds:
        queue.put_nowait(feed)

    workers = []
    for i in range(worker_count):
        w = Worker(queue)
        workers.append(w)
        w.start()
    for w in workers:
        w.join()


def rsspull_serial(feeds):
    for feed in feeds:
        feed.sendNewEntries()


def main():
    rsspull('~/.rsspull')
