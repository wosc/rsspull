from ws.rsspull.feed import Feed, Entry
import os
import pkg_resources
import shutil
import tempfile
import unittest


try:
    from email.Header import decode_header
except ImportError:
    from email.header import decode_header


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

        self.assertEquals('Tim Bray', feed.author)
        self.assertEquals(20, len(entries))
        self.assertEquals('Moose Camp', entries[0].title)

        msg = entries[0].to_mail()
        subject = decode_header(msg['Subject'])[0]
        self.assertEquals(
            'Moose Camp', subject[0].decode(subject[1] or 'ascii'))
        self.assertEquals('Tim Bray <rsspull@localhost>', msg['From'])

    def test_special_cases(self):
        feed = Feed('samruby', 'http://www.intertwingly.net/blog/index.atom')
        shutil.copy(
            pkg_resources.resource_filename(__name__, 'fixture/samruby.xml'),
            self.tmpdir)
        entries = feed.parse()

        self.assertEquals(0, entries[0].resolved_link.find(
            'http://www.intertwingly.net/blog'))

    def test_parse_opml(self):
        feeds = Feed.parseOPML(pkg_resources.resource_filename(
            __name__, 'fixture/feeds.opml'))
        self.assertEquals(3, len(feeds))
        self.assertEquals('ongoing', feeds[0].name)
        self.assertEquals(
            'http://www.tbray.org/ongoing/ongoing.atom', feeds[0].url)

        self.assertEquals('Trac_Example', feeds[2].name)
        self.assertEquals(('user', 'password'), feeds[2].auth)
        self.assert_(os.path.exists(os.path.join(
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
        self.assert_(not entry.seen)
        entry.seen = True
        self.assert_(entry.seen)

        feed, entry = create()
        self.assert_(entry.seen)
