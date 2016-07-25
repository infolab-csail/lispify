"""
Lispify converts Python objects into Lisp-like encoded strings that are
interpretable in Common Lisp.

Use the 'lispify' function to encode a Python object.
To create a new way of interpreting data subclass the LispType class.

Prefix your class with an underscore (_) if it is an intermediate representation
so that the lispify method ignores it.
"""

from numbers import Number
from six import string_types
import warnings

from .util import subclasses, camel_case_to_lisp_name


# For fully deterministic lisp types use this priority.
MIN_PRIORITY = 0
MAX_PRIORITY = 15


def mid_priority():
    """
    Just count. Later classes override previous ones.
    """

    for i in range(MIN_PRIORITY + 1, MAX_PRIORITY):
        yield i

    while True:
        warnings.warn("Increase MAX_PRIORITY")
        yield i

MID_PRIORITY = mid_priority()


class LispType(object):

    """
    A LispType is a Lisp-like encoded string that is interpretable in
    Common Lisp. Its `val` attribute is a Python object.

    Note that not only answers but also questions are lispified.

    To use this subclass it and provide any of the following:

    - val_str: string representation
    - should_parse
    - parse_val
    """

    priority = 0
    literal = False

    def __init__(self, val):
        """
        Lispify a piece of data. Throws ValueError on failure.
        """

        self.val = val

        if self.should_parse():
            self.val = self.parse_val(val)
        else:
            raise ValueError("failed to lispify %s" % str(self.val))

    def should_parse(self):
        """
        If this returns False, LispType is invalid whatever the value.
        """

        return True

    def parse_val(self, val):
        """
        Override this to have special value manipulation.
        """

        return val

    def __repr__(self):
        r = u"<%s object %s>" % (self.__class__.__name__,
                                 self.__str__())
        return r.encode('utf-8')

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u"%s" % self.val_str()

    def val_str(self):
        return unicode(self.val)

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        # compare LispType objects based on their string representation
        if isinstance(other, self.__class__):
            return self.__str__() == other.__str__()
        elif isinstance(other, string_types):
            return self.__str__() == other

        return False

    def __hash__(self):
        return hash(self.__str__())


class LispString(LispType):
    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, string_types)

    def val_str(self):
        v = self.val.replace('"', '\\"')  # escape double quotes
        v = u'"{0}"'.format(v)
        return v


class LispList(LispType):

    """
    This is coordinates and other things like that
    """

    priority = next(MID_PRIORITY)
    literal = True

    def should_parse(self):
        return hasattr(self.val, '__iter__')

    def erepr(self, v):
        if isinstance(v, LispType):
            return unicode(v)

        try:
            return unicode(lispify(v))
        except NotImplementedError:
            return repr(v)

    def val_str(self):
        return u"(%s)" % (" ".join([self.erepr(v) for v in self.val]))

    def __contains__(self, val):
        return (self.erepr(val) in map(self.erepr, self.val))


class LispDict(LispType):

    """
    Get a lispy dictionary of non-None items.
    """

    priority = next(MID_PRIORITY)

    def should_parse(self):
        return isinstance(self.val, dict)

    def val_str(self):
        pairs = sorted(self.val.items())
        return u'(%s)' % self._plist(pairs)

    def _plist(self, pairs):
        """
        A lispy plist without the parens.
        """

        return " ".join(list(self._paren_content_iter(pairs)))

    def _kv_pair(self, k, v):
        if k is None:
            return u"%s" % v

        if isinstance(k, string_types):
            return u":%s %s" % (k, v)

    def _paren_content_iter(self, pairs):
        for k, v in pairs:
            if v is not None:
                # XXX: NastyHack(TM). Replace the nonbreaking space
                # with a space.
                yield self._kv_pair(k, lispify(v))


class LispDate(LispDict):

    """
    Special LispDict that indicates a date.
    Note: YOU are responsible for parsing the date into the format that
    you want (e.g. yyyymmdd) using overlay framework or whatever.
    """

    priority = next(MID_PRIORITY)

    # dictionary keys that indicate date format should be treated differently
    keywords = ["yyyymmdd"]

    def should_parse(self):
        if isinstance(self.val, dict):
            if any([(kw in self.val) for kw in self.keywords]):
                return True

    def _paren_content_iter(self, pairs):
        for k, v in pairs:
            if v is not None:
                if k in self.keywords:
                    yield self._kv_pair(k, v)
                else:
                    yield self._kv_pair(k, lispify(v))


class LispError(LispType):

    """
    An error with a symbol. The expected value should be an exception
    with the class name as desired symbol name and the following attributes:
    :message  a message for internal debugging (used for Python exceptions)
    :reply    a reply message that is okay to show users
              (e.g. death-date for a person that is still alive)
    """

    priority = MAX_PRIORITY

    def should_parse(self):
        return isinstance(self.val, Exception)

    def val_str(self):
        symbol = camel_case_to_lisp_name(type(self.val).__name__)
        kw = self.val.__dict__
        if self.val.message:
            kw.update({'message': self.val.message})

        if kw:
            return u"(:error {symbol} {keys})".format(
                symbol=symbol,
                keys=self._plist(kw.items())
            )
        else:
            return u"(:error %s)" % symbol

    def _plist(self, pairs):
        return " ".join(list(self._paren_content_iter(pairs)))

    def _kv_pair(self, k, v):
        if k is None:
            return u"%s" % v

        if isinstance(k, string_types):
            return u":%s %s" % (k, v)

    def _paren_content_iter(self, pairs):
        for k, v in pairs:
            if v is not None:
                yield self._kv_pair(k, lispify(v))

    def __nonzero__(self):
        """
        Errors should count as zeros so that you can check for an answer with

        if potential_error_or_none:
            # do stuff
        """

        return False


class _LispLiteral(LispType):

    """
    Lisp literals. These are not.
    """
    priority = MAX_PRIORITY
    literal = True


class LispKeyword(_LispLiteral):

    """
    Just a keyword. No content.
    """

    def should_parse(self):
        return isinstance(self.val, string_types) and self.val.startswith(':') \
            and ' ' not in self.val

    def val_str(self):
        return self.val


class LispBool(_LispLiteral):

    """
    Lispify a boolean value
    """

    def should_parse(self):
        return isinstance(self.val, bool)

    def val_str(self):
        return u't' if self.val else u'nil'


class LispNone(_LispLiteral):

    """
    Lispified none object
    """

    def should_parse(self):
        return self.val is None

    def val_str(self):
        return u'nil'


class LispNumber(_LispLiteral):

    def should_parse(self):
        return isinstance(self.val, Number)

    def val_str(self):
        return str(self.val)


WIKIBASE_LISP_TYPES = subclasses(LispType, instantiate=False)


def lispify(obj):
    """
    Return a Lisp-like encoded string.
    """

    if isinstance(obj, LispType):
        return obj

    for T in WIKIBASE_LISP_TYPES:
        try:
            return T(obj)
        except ValueError:
            pass

    raise NotImplementedError(
        "Implement LispType for val: %s or provide fallback error." % obj)

__all__ = ['lispify']
