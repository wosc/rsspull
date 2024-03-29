from ws.rsspull.feed import Feed
import os
import os.path
import shutil
import tempfile
import unittest


class FeedTest(unittest.TestCase):

    def setUp(self):
        Feed.verbose = False
        self.tmpdir = tempfile.mkdtemp()
        Feed.workdir = self.tmpdir
        os.rmdir(self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_download(self):
        feed = Feed('ongoing', 'http://www.tbray.org/ongoing/ongoing.atom')
        xml = os.path.join(self.tmpdir, 'ongoing.xml')

        feed.download()
        self.assertTrue(os.path.exists(xml))
        self.assertTrue(feed.updated())
        before = os.stat(xml).st_mtime
        feed.download()
        after = os.stat(xml).st_mtime
        self.assertFalse(feed.updated())
        self.assertEqual(before, after)

    def test_not_updated_even_if_no_etag(self):
        # heise doesn't do ETAG
        feed = Feed(
            'heisec', 'https://www.heise.de/security/rss/news-atom.xml')

        feed.download()
        self.assertTrue(feed.updated())
        feed.download()
        self.assertFalse(feed.updated())

    def test_download_error(self):
        feed = Feed('ongoing', 'urks://')
        self.assertRaises(RuntimeError, feed.download)
