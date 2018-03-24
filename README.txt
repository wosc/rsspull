=======
rsspull
=======

rsspull downloads and parses RSS and Atom feeds, converts posts into email
messages, and stores them in Maildirs. This way you can read your feeds using
an email client (I use `claws`_, so I can access mailing lists, newsgroups and
feeds all in one application). The heavy lifting is performed by the awesome
`feedparser`_ library.

.. _`claws`: http://claws-mail.org/
.. _`feedparser`: https://pypi.python.org/pypi/feedparser



Installation
============

rsspull requires at least Python 2.6 (and won't work under Python 3 yet).
You can install it from PyPI like this::

    $ pip install ws.rsspull

You need to create a configuration file in ``~/.rsspull/config``, like::

    [global]
    target = ~/Maildir/rss
    target_type = maildir
    logfile = ~/.rsspull/log
    workers = 1

For low-volume applications you can also send the emails via SMTP (localhost)
instead::

    [global]
    target = test@example.com
    target_type = smtp

List the feeds you want to pull in an OPML file at ``~/.rsspull/feeds.opml``::

    <?xml version="1.0" encoding="utf-8"?>
    <opml version="1.1">
      <head>
        <title>feeds.opml</title>
        <ownerName>rsspull</ownerName>
        <ownerEmail>rsspull@localhost</ownerEmail>
      </head>
      <body>
        <outline text="tech">
          <outline text="ongoing" xmlUrl="http://www.tbray.org/ongoing/ongoing.atom" />
        </outline>
        <outline text="general">
          <outline text="heisec" xmlUrl="http://www.heise.de/security/news/news.rdf" />
          <outline text="trac_example" xmlUrl="https://example.com/trac/timeline?milestone=on&amp;ticket=on&amp;changeset=on&amp;wiki=on&amp;max=10&amp;daysback=90&amp;format=rss" auth="user:password"/>
        </outline>
      </body>
    </opml>

Notes about the format:

* You can group your feeds (using nested ``<outlines>``), this does not matter
  to rsspull.
* The ``text`` attribute is used as the folder name, relative to the
  ``maildir`` setting in ``~/.rsspull/config``. If you run rsspull on an IMAP
  server, you can create folder hierarchies by using something like
  ``text=".rss.tech.ongoing"`` (check you IMAP server documentation how it
  represents folder hierarchies. The example with dots works for Courier,
  others might use actual subfolders, and so on).
* Basic authentication is supported with the ``auth`` attribute.
* You can use ``file://`` URLs.

Then simply run::

    $ rsspull

to download the feeds.

You can pass ``rsspull --confdir /path/to/config`` to use a different location
than ``~/.rsspull``.


Features
========

* Uses ``If-Modified-Since`` HTTP headers to avoid downloading a feed that has
  not changed.
* Addds a ``Content-Location`` header to each message that contains the URL of
  that post. I bound the following script to [return] in claws to open the
  current entry in a webbrowser::

    #!/bin/bash
    URL=`sed -ne '/^Content-Location/s/.*: //p' $1 | head -n 1`
    if [ -n "$URL" ]; then
        mozilla $URL &> /dev/null
    fi

* Entries are converted to multipart messages, one with the original HTML and
  one converted into markdown-like plaintext (via `html2text`_), so most of the
  time opening in a browser isn't even necessary since you can read the post
  right in the email client.
* Can use several worker threads to download and parse feeds to increase
  performance, since quite some time is spent waiting for downloads to complete
  (the ``workers`` setting in ``~/.rsspull/config``).
* Has been in daily usage since 2007, so it definitely Works For Me(tm).


.. _`html2text`: https://pypi.python.org/pypi/html2text
