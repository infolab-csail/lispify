#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_util
----------------------------------

Tests for `util` module.
"""


try:
    import unittest2 as unittest
except ImportError:
    import unittest

from lispify import util


class TestUtil(unittest.TestCase):

    def test_camel_case_to_lisp_name(self):
        name = util.camel_case_to_lisp_name("UnknownAttribute")
        self.assertEqual(name, "unknown-attribute")
        name = util.camel_case_to_lisp_name("ResourceNotFound")
        self.assertEqual(name, "resource-not-found")


if __name__ == '__main__':
    unittest.main()
