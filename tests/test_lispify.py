#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lispify
----------------------------------

Tests for `lispify` module.
"""

from sys import version_info

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from lispify.lispify import lispify


def to_lisp_string(obj):
    return str(lispify(obj))


class TestLispify(unittest.TestCase):

    def test_string(self):
        self.assertEqual(to_lisp_string("foo"),
                         '"foo"')

    def test_string_escaped(self):
        self.assertEqual(to_lisp_string('foo \\ "bar"'),
                         '"foo \\ \\"bar\\""')

    def test_encodings(self):
        if version_info < (3,):
            # python 2 behavior
            self.assertEqual(to_lisp_string(u"föø ” "),
                             u'"föø ” "'.encode('utf-8'))
            self.assertEqual(unicode(lispify(u"föø ” ")),
                             u'"föø ” "')
        else:
            # python 3 behavior
            self.assertEqual(to_lisp_string(u"föø ” "),
                             u'"föø ” "')

    def test_list(self):
        l = ['wikipedia-class1', 'wikipedia-class2']
        self.assertEqual(to_lisp_string(l),
                         '("wikipedia-class1" "wikipedia-class2")')

    def test_nested_list(self):
        l = [[0, 'foo'], [1, '"bar"']]
        self.assertEqual(to_lisp_string(l),
                         '((0 "foo") (1 "\\"bar\\""))')

    def test_nested_tuple(self):
        # this test needs to be separated from nested list because tuples
        # are used in string formatting (see #222 for an example of failure)
        t = ('foo', ('bar', 'baz'))
        self.assertEqual(to_lisp_string(t),
                         '("foo" ("bar" "baz"))')

    def test_double_nested_list(self):
        l = [[0, ['v0', 'foo']], [1, ['v1', 'bar']]]
        self.assertEqual(to_lisp_string(l),
                         '((0 ("v0" "foo")) (1 ("v1" "bar")))')

    def test_list_of_dict(self):
        l = [{'foo': 'bar'}, {'foo': 'baz'}]
        self.assertEqual(to_lisp_string(l),
                         '((:foo "bar") (:foo "baz"))')

    def test_list_contains(self):
        ll = lispify(["1", "3"])
        self.assertIn("1", ll)
        self.assertNotIn(1, ll)

    def test_date_simple(self):
        date = {'yyyymmdd': '00000808'}
        self.assertEqual(to_lisp_string(date),
                         '(:yyyymmdd 00000808)')

    def test_date_multiple_keys(self):
        date = {'yyyymmdd': '19491001', 'html': 'Oct 1, 1949'}
        self.assertEqual(to_lisp_string(date),
                         '(:html "Oct 1, 1949" :yyyymmdd 19491001)')

    def test_bool(self):
        self.assertEqual(to_lisp_string(True), 't')
        self.assertEqual(to_lisp_string(False), 'nil')

    def test_keyword(self):
        self.assertEqual(to_lisp_string(':feminine'),
                         ':feminine')

    def test_string_not_keyword(self):
        self.assertEqual(to_lisp_string(':not a keyword'),
                         '":not a keyword"')

    def test_dict(self):
        self.assertEqual(to_lisp_string({'a': 1, 'b': "foo"}),
                         '(:a 1 :b "foo")')

    def test_dict_with_escaped_string(self):
        self.assertEqual(to_lisp_string({'a': 1, 'b': '"foo"'}),
                         '(:a 1 :b "\\"foo\\"")')

    def test_dict_with_list(self):
        self.assertEqual(to_lisp_string({'a': 1, 'b': ['foo', 'bar']}),
                         '(:a 1 :b ("foo" "bar"))')

    def test_error_from_exception(self):
        err = ValueError('Wrong thing')
        self.assertEqual(to_lisp_string(err),
                         '(:error value-error :message "Wrong thing")')

        err = NotImplementedError()
        self.assertEqual(to_lisp_string(err),
                         '(:error not-implemented-error)')

    def test_none(self):
        self.assertEqual(to_lisp_string(None), 'nil')

    def test_number(self):
        self.assertEqual(to_lisp_string(5), '5')

    def test_lispified(self):
        val = {"hello": "world"}
        self.assertEqual(lispify(val), lispify(lispify(val)))

    def test_partially_lispified(self):
        val = [lispify(1), lispify(2)]
        self.assertEqual(to_lisp_string(val), '(1 2)')

    @unittest.expectedFailure
    def test_unimplemented(self):
        lispify(lambda x: x)

if __name__ == '__main__':
    unittest.main()
