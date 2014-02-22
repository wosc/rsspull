from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from email.MIMEText import MIMEText
from html2text import html2text
import datetime
import email.utils
import feedparser
import logging
import md5
import os
import os.path
import urllib2
import urlparse
import ws.rsspull.maildir
import ws.rsspull.util
import xml.dom.minidom


USER_AGENT = ('Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.2)'
              ' Gecko/20070220 Firefox/2.0.0.2')
log = logging.getLogger(__name__)


class Entry(object):

    def __init__(self, feed, item):
        self.feed = feed
        self.item = item

        self.body = self._findValue(
            'content body content_encoded description summary summary_detail')
        self.body = self._value(self.body)
        self.timestamp = self._findValue(
            'published_parsed modified_parsed created_parsed')
        if self.timestamp:
            self.timestamp = datetime.datetime(*self.timestamp[:5])
        else:
            self.timestamp = datetime.datetime.now()

        hash = ''.join([self.link, self.title, self.feed.url])
        self.hash = md5.new(hash.encode('utf-8', 'replace')).hexdigest()

        # Hi, my name is Sam Ruby and I exercise any and all wrinkles
        # of the Atom protocol, thereby f***ing up everyone's parser
        self.resolved_link = self.link
        if self.resolved_link.find('http') != 0:
            self.resolved_link = urlparse.urljoin(self.feed.link, self.link)
        if self.resolved_link.find('http') != 0:
            try:
                parent = filter(lambda l: l.rel == 'self', self.feed.links)[0]
                self.resolved_link = urlparse.urljoin(parent.href, self.link)
            except IndexError:
                pass

    # delegates to feedparser
    def __getattr__(self, name):
        return getattr(self.item, name)

    def to_mail(self):
        message = MIMEMultipart('alternative')

        try:
            author = self.author
        except AttributeError:
            try:
                author = self.feed.author
            except AttributeError:
                try:
                    author = self.feed.title
                except AttributeError:
                    author = self.feed.name

        message['From'] = '%s <rsspull@localhost>' % author
        message['To'] = Feed.recipient
        message['Date'] = self.timestamp.strftime(
            '%a, %d %b %Y %H:%M:%S +0000')
        # XXX: msgid?
        message['Subject'] = ws.rsspull.util.header(self.title)
        message['X-RSS-Id'] = self.feed.name
        message['Content-Location'] = self.resolved_link

        body = self.body
        body = ws.rsspull.util.expandNumEntities(body)
        body = ws.rsspull.util.fixQuotes(body)
        body = html2text(body).strip()
        body += '\n\n' + 'Link: [ ' + self.resolved_link + ' ]\n'

        text_part = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
        html_part = MIMENonMultipart('text', 'html', charset='utf-8')
        html_part.set_payload(self.body.encode('utf-8'))

        message.attach(text_part)
        message.attach(html_part)
        return message

    def _findValue(self, candidates):
        for k in candidates.split():
            try:
                body = getattr(self.item, k)
                if body:
                    return body
            except AttributeError:
                pass

    def _value(self, x):
        if isinstance(x, basestring):
            return x
        elif isinstance(x, list):
            try:
                return x[0]['value']
            except:
                return ''
        else:
            return ''

    def setSeen(self, seen):
        if seen:
            fd = open(self.feed.cache, 'a')
            fd.write('%s %s\n'.encode('utf8') % (self.hash, self.link))
            fd.close()

    def getSeen(self):
        cache = open(self.feed.cache).read()
        return self.hash in cache

    seen = property(getSeen, setSeen)


class Feed(object):

    workdir = None
    maildir = None

    recipient = 'rsspull <rsspull@localhost>'

    @staticmethod
    def parseOPML(config):
        doc = xml.dom.minidom.parse(config)
        feeds = []
        for e in doc.getElementsByTagName('outline'):
            url = e.getAttribute('xmlUrl')
            if url != '':
                name = e.getAttribute('text')
                if name == '':
                    raise 'Feed without a name: %r' % e
                feed = Feed(name, url)
                feeds.append(feed)

                auth = e.getAttribute('auth')
                if auth != '':
                    feed.auth = auth
        return feeds

    def __init__(self, name, url):
        if not os.path.exists(Feed.workdir):
            os.makedirs(Feed.workdir)

        self.name = name.replace(' ', '_')
        self.url = url
        self.feed = None
        self.auth = None

        self.file = os.path.join(Feed.workdir, '%s.xml' % self.name)
        self.cache = os.path.join(Feed.workdir, '%s.cache' % self.name)
        if not os.path.exists(self.cache):
            open(self.cache, 'w').close()
        self.md5 = os.path.join(Feed.workdir, '%s.xml.md5' % self.name)
        if not os.path.exists(self.md5):
            open(self.md5, 'w').close()

    # delegates to feedparser
    def __getattr__(self, name):
        return getattr(self.feed, name)

    def download(self):
        headers = {
            'User-Agent': USER_AGENT
        }
        if os.path.exists(self.file):
            headers['If-Modified-Since'] = email.utils.formatdate(
                os.stat(self.file).st_mtime)
        if self.auth:
            headers['Authorization'] = 'Basic %s' % self.auth.encode('base64')

        log.info('Downloading %s <%s>' % (self.name, self.url))

        try:
            # XXX wrap in timeout?
            response = urllib2.urlopen(
                urllib2.Request(self.url, headers=headers), timeout=30)
        except Exception, e:
            if isinstance(e, urllib2.HTTPError) and e.code == 304:
                # not modified
                return
            raise RuntimeError('Downloading %s from %s failed: %s' % (
                self.name, self.url, str(e)))
        if response.code == 304:
            return
        if response.code == 200 or response.code is None:
            open(self.file, 'w').write(response.read())
        else:
            raise RuntimeError('Downloading %s from %s failed: %s' % (
                self.name, self.url, response.read()))

    def updated(self):
        new = md5.new(open(self.file).read()).hexdigest()
        old = open(self.md5).read()
        if new == old:
            return False
        open(self.md5, 'w').write(new)
        return True

    def parse(self):
        log.info('Parsing %s' % self.name)
        parsed = feedparser.parse(self.file)
        self.feed = parsed.feed
        entries = [Entry(self, e) for e in parsed.entries]
        self.entries = entries
        return self.entries

    def sendNewEntries(self):
        try:
            self.download()
            if not self.updated():
                log.info('No change in %s' % self.name)
                return
            self.parse()
            count = 0
            for entry in self.entries:
                if entry.seen:
                    continue
                self.send(entry.to_mail())
                entry.seen = True
                count += 1
            log.info('%d new items in %s' % (count, self.name))
        except Exception, e:
            log.exception(e)

    def send(self, email):
        maildir = ws.rsspull.maildir.Maildir(
            os.path.join(self.maildir, self.name), create=True)
        writer = maildir.newMessage()
        writer.write(email.as_string(unixfrom=True))
        writer.commit()
