from html2text import html2text
from htmlentitydefs import entitydefs
import email.Header
import logging
import os
import re


def intEnt(m):
    m = int(m.groups(1)[0])
    return unichr(m)


def xEnt(m):
    m = int(m.groups(1)[0], 16)
    return unichr(m)


def nameEnt(m):
    m = m.groups(1)[0]
    if m in entitydefs.keys():
        return entitydefs[m].decode('latin1')
    else:
        return '&' + m +';'


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


def header(text):
    if not text:
        text = ''
    if not isinstance(text, unicode):
        text = text.decode('latin1')
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    try:
        text = html2text(text).strip()
    except UnicodeError:
        pass
    return str(email.Header.make_header([(text, 'utf-8')]))


def setupLogging(directory=None):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    logfile = logging.FileHandler(os.path.join(directory, 'log'))
    logfile.setLevel(logging.INFO)
    logfile.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    root.addHandler(logfile)
