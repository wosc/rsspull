from email.header import make_header
from html.entities import entitydefs
from html2text import HTML2Text
import logging
import re


def intEnt(m):
    m = int(m.groups(1)[0])
    return chr(m)


def xEnt(m):
    m = int(m.groups(1)[0], 16)
    return chr(m)


def nameEnt(m):
    m = m.groups(1)[0]
    if m in entitydefs.keys():
        val = entitydefs[m]
        if not isinstance(val, str):
            val = val.decode('latin1')
        return val
    else:
        return '&' + m + ';'


def expandNumEntities(text):
    text = re.sub(r'&#(\d+);', intEnt, text)
    text = re.sub(r'&#[Xx](\w+);', xEnt, text)
    text = re.sub(r'&(.*?);', nameEnt, text)
    return text


def fixQuotes(text):
    text = text.replace(u'\u2026', '...')
    text = text.replace(u'\u2018', '\'')
    text = text.replace(u'\u2019', '\'')
    text = text.replace(u'\u201C', '\'')
    text = text.replace(u'\u201D', '\'')
    return text


def html2text(text):
    h = HTML2Text()
    h.inline_links = False
    return h.handle(text)


def header(text):
    if not text:
        text = ''
    if not isinstance(text, str):
        text = text.decode('latin1')
    try:
        text = html2text(text).strip()
    except UnicodeError:
        pass
    return make_header([(text, 'utf-8')]).encode()


def setupLogging(logfile='log'):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    logfile = logging.FileHandler(logfile)
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    root.addHandler(logfile)
