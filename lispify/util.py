from itertools import chain
import re


def subclasses(cls):
    """
    A list of subclasses of cls.
    """

    lcls = cls.__subclasses__()
    rcls = lcls + list(chain.from_iterable([c.__subclasses__() for c in lcls]))
    for c in rcls:
        assert isinstance(c.priority, int), \
            "type(%s . priority) = %s != int" % (repr(c), type(c.priority.name))

    clss = sorted(rcls, key=lambda c: c.priority, reverse=True)

    return [C for C in clss
            if not C.__name__.startswith("_")]


def camel_case_to_lisp_name(text):
    """
    Converts CamelCase text to standard lisp hyphenated text
    e.g., "educationalInstitution" -> "educational-institution"
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s).lower()

