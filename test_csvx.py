import unittest

import csvx as m

import textwrap
from externals.fake import Fake as MemExternal


def records_from_text(text):
    return [
        tuple(line.strip().split(u','))
        for line in text.splitlines()
        ]


class Test_records_from_text(unittest.TestCase):

    def test(self):
        self.assertListEqual(
            [
                (u'header1', u'header2'),
                (u'value1', u'')],
            records_from_text(u'''\
                header1,header2
                value1, '''))


class Test_fix_missing_columns(unittest.TestCase):

    def test_well_formed_input_remains_as_is(self):
        self.assertListEqual(
            records_from_text(u'''\
                header1,header2
                value1,value2 '''),
            list(
                m.fix_missing_columns(
                    records_from_text(u'''\
                        header1,header2
                        value1,value2 '''))))

    def test_short_records_are_padded_with_empty_strings(self):
        self.assertListEqual(
            records_from_text(u'''\
                header1,header2
                value1, '''),
            list(
                m.fix_missing_columns(
                    records_from_text(u'''\
                        header1,header2
                        value1 '''))))

    def test_longer_than_header_row_raise_ValueError(self):
        with self.assertRaises(ValueError):
            list(
                m.fix_missing_columns(
                    records_from_text(u'''\
                        header1,header2
                        value1,value2,value3
                        ''')))


class Test_select(unittest.TestCase):

    def assert_selects(self, result_csv, input_csv, columns):
        self.assertListEqual(
            records_from_text(result_csv),
            list(
                m.select(
                    records_from_text(input_csv),
                    columns.split(u','))))

    def test_select_one_column(self):
        input_csv = u'''a,b,c
            a,1,c
            a,2,d
            x,3,x'''
        self.assertListEqual(
            [u'1', u'2', u'3'],
            list(
                m.select(
                    records_from_text(input_csv),
                    [u'b'])))

    def test_select_no_columns_is_error(self):
        input_csv = u'''a,b
                a,1
                a,2
                x,3'''

        with self.assertRaises(Exception):
            m.select(records_from_text(input_csv), [])

    def test_select_columns_in_reverse_order(self):
        self.assert_selects(
            result_csv=u'''1,a
                2,a
                3,x''',
            input_csv=u'''a,b,c
                a,1,c
                a,2,d
                x,3,x''',
            columns=u'b,a')

    def test_select_a_column_multiple_times(self):
        self.assert_selects(
            result_csv=u'''1,1
                2,2
                3,3''',
            input_csv='''a,b,c
                a,1,c
                a,2,d
                x,3,x''',
            columns=u'b,b')


class Test_selectx(unittest.TestCase):

    def test(self):
        csv_external = MemExternal()
        csv_external.content = textwrap.dedent(
            u'''\
            a,b,c
            a,1,c
            a,2,d
            x,3,x''').encode('utf-8')
        self.assertListEqual(
            [u'1', u'2', u'3'],
            list(m.selectx(csv_external, [u'b'])))
