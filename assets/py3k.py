# Imports
import sys

# Variables
PY3K = sys.version_info >= (3, 0)

# Try Catches
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
	from urllib import urlopen
except ImportError:
	from urllib.request import urlopen
try:
    from io import BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO
try:
    from hashlib import md5
except ImportError:
    try:
        from md5 import md5
    except ImportError:
        md5 = None
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        Image = None
try:
	from HTMLParser import HTMLParser
except ImportError:
	from html.parser import HTMLParser

# Checks
if PY3K:
    basestring = str
    unicode = str
    ord = lambda x: x
else:
    basestring = basestring
    unicode = unicode
    ord = ord

# Functions
def b(s):
    if isinstance(s, basestring):
        return s.encode("latin1")
    elif isinstance(s, int):
        if PY3K:
            return bytes([s])
        else:
            return chr(s)
			
def exception():
    return sys.exc_info()[1]

def hashpath(fn):
    h = md5()
    if PY3K:
        h.update(fn.encode("UTF-8"))
    else:
        h.update(fn)
    return h.hexdigest()
