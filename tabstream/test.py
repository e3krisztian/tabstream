import unittest

import tabstream as m


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


class Test_pad(unittest.TestCase):

    def test_well_formed_input_remains_as_is(self):
        self.assertListEqual(
            records_from_text(u'''\
                header1,header2
                value1,value2 '''),
            list(
                m.pad(
                    records_from_text(u'''\
                        header1,header2
                        value1,value2 '''))))

    def test_short_records_are_padded_with_empty_strings(self):
        self.assertListEqual(
            records_from_text(u'''\
                header1,header2
                value1, '''),
            list(
                m.pad(
                    records_from_text(u'''\
                        header1,header2
                        value1 '''))))

    def test_longer_than_header_row_raise_ValueError(self):
        with self.assertRaises(ValueError):
            list(
                m.pad(
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


class Test_make_field_adder(unittest.TestCase):

    def test_no_parameters(self):
        def constant():
            return 'c'

        filter = m.make_field_adder('const', constant, [])
        self.assertListEqual(
            [
                ('a', 'b', 'const'),
                ('a', 'b', 'c'),
                (1.1, 3, 'c')
            ],
            list(filter([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))

    def test_single_parameter(self):
        def dup(input_field):
            return input_field + input_field
        filter = m.make_field_adder('2a', dup, ['a'])
        self.assertListEqual(
            [
                ('a', 'b', '2a'),
                ('a', 'b', 'aa'),
                (1.1, 3, 2.2)
            ],
            list(filter([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))

    def test_two_parameters(self):
        def plus(input_field1, input_field2):
            return input_field1 + input_field2
        filter = m.make_field_adder('b+a', plus, ['b', 'a'])
        self.assertListEqual(
            [
                ('a', 'b', 'b+a'),
                ('a', 'b', 'ba'),
                (1.1, 3, 4.1)
            ],
            list(filter([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))


class Test_field_adder(unittest.TestCase):

    def test_no_parameters(self):
        @m.field_adder
        def add_const():
            return 'c'

        self.assertListEqual(
            [
                ('a', 'b', 'const'),
                ('a', 'b', 'c'),
                (1.1, 3, 'c')
            ],
            list(add_const([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))

    def test_single_parameter(self):
        @m.field_adder
        def add_2a(a):
            return a + a

        self.assertListEqual(
            [
                ('a', 'b', '2a'),
                ('a', 'b', 'aa'),
                (1.1, 3, 2.2)
            ],
            list(add_2a([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))

    def test_two_parameters(self):
        @m.field_adder
        def add_x(b, a):
            return b + a

        self.assertListEqual(
            [
                ('a', 'b', 'x'),
                ('a', 'b', 'ba'),
                (1.1, 3, 4.1)
            ],
            list(add_x([
                ('a', 'b'),
                ('a', 'b'),
                (1.1, 3)
                ])))


class Test_delete_fields(unittest.TestCase):

    def test(self):
        delete_a_c = m.delete_fields('a', 'c')
        self.assertListEqual(
            [
                ('b', 'd'),
                (2, 4)
            ],
            list(delete_a_c([
                ('a', 'b', 'c', 'd'),
                (1, 2, 3, 4)
                ])))

    def test_delete_non_existing(self):
        delete_a_c = m.delete_fields('a', 'c')
        self.assertListEqual(
            [
                ('b',),
                (2,)
            ],
            list(delete_a_c([
                ('a', 'b'),
                (1, 2)
                ])))


class Test_rename(unittest.TestCase):

    # output column order remains the same
    # duplicated columns are put next to each other
    # duplicated column labels are ordered:
    #   first: original label (if still there)
    #   others: alphabetically

    def test_in_place(self):
        transform = m.rename(a1='a', b1='b')
        self.assertListEqual(
            [
                ('a1', 'b1', 'c', 'd'),
                (1, 2, 3, 4)
            ],
            list(transform([
                ('a', 'b', 'c', 'd'),
                (1, 2, 3, 4)
                ])))

    def test_overwrite_existing_column(self):
        transform = m.rename(b='a')
        self.assertListEqual(
            [
                ('b', 'c', 'd'),
                (1, 3, 4)
            ],
            list(transform([
                ('a', 'b', 'c', 'd'),
                (1, 2, 3, 4)
                ])))

    def test_swap_labels(self):
        transform = m.rename(b='a', a='b')
        self.assertListEqual(
            [
                ('b', 'a', 'c', 'd'),
                (1, 2, 3, 4)
            ],
            list(transform([
                ('a', 'b', 'c', 'd'),
                (1, 2, 3, 4)
                ])))

    def test_rename_with_special_characters(self):
        transform = m.rename({'new @!': 'old !'})
        self.assertListEqual(
            [
                ('a', 'b', 'new @!', 'd'),
                (1, 2, 3, 4)
            ],
            list(transform([
                ('a', 'b', 'old !', 'd'),
                (1, 2, 3, 4)
                ])))

    def test_duplicate_under_another_name(self):
        transform = m.rename(d='a', a='a')
        self.assertListEqual(
            [
                ('a', 'd', 'b'),
                (1, 1, 2)
            ],
            list(transform([
                ('a', 'b'),
                (1, 2)
                ])))


class Test_pipe(unittest.TestCase):

    def test_order_of_transformations(self):
        def add_a(stream):
            return (val + 'a' for val in stream)

        def add_b(stream):
            return (val + 'b' for val in stream)

        transform = m.pipe(add_a, add_b)

        self.assertListEqual(
            ['1ab', '2ab'],
            list(transform(['1', '2'])))
