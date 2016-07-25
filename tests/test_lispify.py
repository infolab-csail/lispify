#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lispify
----------------------------------

Tests for `lispify` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from lispify.lispify import lispify


class TestLispify(unittest.TestCase):

    def test_string(self):
        self.assertEqual(lispify("foo"), '"foo"')

    def test_string_escaped(self):
        self.assertEqual(lispify('foo \\ "bar"'), '"foo \\ \\"bar\\""')

    def test_encodings(self):
        self.assertEqual(str(lispify(u"föø ” ")), u'"föø ” "'.encode('utf-8'))
        self.assertEqual(unicode(lispify(u"föø ” ")), u'"föø ” "')

    def test_list(self):
        l = ['wikipedia-class1', 'wikipedia-class2']
        self.assertEqual(lispify(l), '("wikipedia-class1" "wikipedia-class2")')

    def test_nested_list(self):
        l = [[0, 'foo'], [1, '"bar"']]
        self.assertEqual(lispify(l), '((0 "foo") (1 "\\"bar\\""))')

    def test_nested_tuple(self):
        # this test needs to be separated from nested list because tuples
        # are used in string formatting (see #222 for an example of failure)
        t = ('foo', ('bar', 'baz'))
        self.assertEqual(lispify(t), '("foo" ("bar" "baz"))')

    def test_double_nested_list(self):
        l = [[0, ['v0', 'foo']], [1, ['v1', 'bar']]]
        self.assertEqual(lispify(l), '((0 ("v0" "foo")) (1 ("v1" "bar")))')

    def test_list_of_dict(self):
        l = [{'foo': 'bar'}, {'foo': 'baz'}]
        self.assertEqual(lispify(l), '((:foo "bar") (:foo "baz"))')

    def test_list_contains(self):
        ll = lispify(["1", "3"])
        self.assertIn("1", ll)
        self.assertNotIn(1, ll)

    def test_date_simple(self):
        ed = lispify({'yyyymmdd': '00000808'})
        self.assertEqual(ed, '(:yyyymmdd 00000808)')

    def test_date_multiple_keys(self):
        ed = lispify({'yyyymmdd': '19491001', 'html': 'Oct 1, 1949'})
        self.assertEqual(ed, '(:html "Oct 1, 1949" :yyyymmdd 19491001)')

    def test_bool(self):
        self.assertEqual(lispify(True), 't')
        self.assertEqual(lispify(False), 'nil')

    def test_keyword(self):
        self.assertEqual(lispify(':feminine'), ":feminine")

    def test_string_not_keyword(self):
        self.assertEqual(lispify(':not a keyword'), '":not a keyword"')

    def test_dict(self):
        self.assertEqual(lispify({'a': 1, 'b': "foo"}),
                         '(:a 1 :b "foo")')

    def test_dict_with_escaped_string(self):
        self.assertEqual(lispify({'a': 1, 'b': '"foo"'}),
                         '(:a 1 :b "\\"foo\\"")')

    def test_dict_with_list(self):
        self.assertEqual(lispify({'a': 1, 'b': ['foo', 'bar']}),
                         '(:a 1 :b ("foo" "bar"))')

    def test_error_from_exception(self):
        err = lispify(ValueError('Wrong thing'))
        self.assertEqual(err, '(:error value-error :message "Wrong thing")')

    def test_none(self):
        self.assertEqual(lispify(None), 'nil')

    def test_number(self):
        self.assertEqual(lispify(5), '5')

    def test_lispified(self):
        val = {"hello": "world"}
        self.assertEqual(lispify(val), lispify(lispify(val)))

    @unittest.expectedFailure
    def test_unimplemented(self):
        lispify(lambda x: x)

if __name__ == '__main__':
    unittest.main()
