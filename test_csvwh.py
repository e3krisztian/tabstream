import unittest
import io
import textwrap
import csvwh as m


def stringio(text):
    return io.StringIO(textwrap.dedent(text))


class Test_Reader(unittest.TestCase):

    def test_header_is_not_passed_through(self):
        file = stringio(u'''\
            header1,header2
            value1,value2
            ''')
        self.assertListEqual(
            [[u'value1', u'value2']],
            list(m.Reader(file)))

    def test_short_input_lines_are_processed(self):
        file = stringio(u'''\
            header1,header2
            value1
            value11,value2
            ''')
        self.assertListEqual(
            [[u'value1', u''], [u'value11', u'value2']],
            list(m.Reader(file)))

    def test_too_many_values_in_record_is_an_error(self):
        file = stringio(u'''\
            header1,header2
            value1,value2,value3
            ''')
        with self.assertRaises(ValueError):
            iter(m.Reader(file)).next()

    def test_select_columns_only_requested_columns_are_available(self):
        file = stringio(u'''\
            header1,header2
            value1,value2
            ''')
        self.assertListEqual(
            [u'value2'],
            list(m.Reader(file).select([u'header2'])))

    def test_select_columns_input_can_be_in_different_order(self):
        file = stringio(u'''\
            header1,header2
            value1,value2
            ''')
        self.assertListEqual(
            [(u'value2', u'value1')],
            list(m.Reader(file).select([u'header2', u'header1'])))
