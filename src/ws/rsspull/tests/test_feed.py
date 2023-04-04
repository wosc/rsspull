from email.header import decode_header
from ws.rsspull.feed import Feed, Entry
import os
import pkg_resources
import shutil
import tempfile
import unittest


class FeedTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Feed.workdir = self.tmpdir
        Feed.recipient = 'nobody@invalid'
        Feed.verbose = False

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_parse_entries(self):
        feed = Feed('ongoing', 'http://www.tbray.org/ongoing/ongoing.atom')
        shutil.copy(
            pkg_resources.resource_filename(__name__, 'fixture/ongoing.xml'),
            self.tmpdir)
        entries = feed.parse()

        self.assertEqual('Tim Bray', feed.author)
        self.assertEqual(20, len(entries))
        self.assertEqual('Moose Camp', entries[0].title)

        msg = entries[0].to_mail()
        subject = decode_header(msg['Subject'])[0]
        self.assertEqual(
            'Moose Camp', subject[0].decode(subject[1] or 'ascii'))
        self.assertEqual('Tim Bray <rsspull@localhost>', msg['From'])

    def test_special_cases(self):
        feed = Feed('samruby', 'http://www.intertwingly.net/blog/index.atom')
        shutil.copy(
            pkg_resources.resource_filename(__name__, 'fixture/samruby.xml'),
            self.tmpdir)
        entries = feed.parse()

        self.assertEqual(0, entries[0].resolved_link.find(
            'http://www.intertwingly.net/blog'))

    def test_parse_opml(self):
        feeds = Feed.parseOPML(pkg_resources.resource_filename(
            __name__, 'fixture/feeds.opml'))
        self.assertEqual(3, len(feeds))
        self.assertEqual('ongoing', feeds[0].name)
        self.assertEqual(
            'http://www.tbray.org/ongoing/ongoing.atom', feeds[0].url)

        self.assertEqual('Trac_Example', feeds[2].name)
        self.assertEqual(('user', 'password'), feeds[2].auth)
        self.assertTrue(os.path.exists(os.path.join(
            self.tmpdir, 'Trac_Example.cache')))

    def test_seen(self):
        class MockItem:
            link = 'http://foo'
            title = 'Title'

        def create():
            feed = Feed('ongoing', 'http://www.tbray.org/ongoing/ongoing.atom')
            feed.author = None
            entry = Entry(feed, MockItem())
            return feed, entry

        feed, entry = create()
        self.assertFalse(entry.seen)
        entry.seen = True
        self.assertTrue(entry.seen)

        feed, entry = create()
        self.assertTrue(entry.seen)
