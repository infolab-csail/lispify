from itertools import chain
import re


def subclasses(cls, instantiate=True, **kw):
    """
    A list of instances of subclasses of cls. Instantiate wit kw and
    return just the classes with instantiate=False.
    """

    lcls = cls.__subclasses__()
    rcls = lcls + list(chain.from_iterable([c.__subclasses__() for c in lcls]))
    for c in rcls:
        assert isinstance(c.priority, int), \
            "type(%s . priority) = %s != int" % (repr(c), type(c.priority.name))

    clss = sorted(rcls, key=lambda c: c.priority, reverse=True)

    if not instantiate:
        return [C for C in clss
                if not C.__name__.startswith("_")]

    return [C(**kw) for C in clss
            if not C.__name__.startswith("_")]


def camel_case_to_lisp_name(name):
    """
    Convert a python CamelCase class name to lisp hyphenated class name.
    """
    words = map(lambda s: s.lower(), re.findall('[A-Z][a-z]*', name))
    lisp_name = '-'.join(words)
    return lisp_name
