import unittest
import io
import textwrap
import csvx as m


def stringio(text):
    return io.StringIO(textwrap.dedent(text))


def h1h2v1v2():
    '''a well known file-like object
    '''
    return stringio(u'''\
        header1,header2
        value1,value2
        ''')


def h1h2v1v2v3v4():
    '''a well known file-like object
    '''
    return stringio(u'''\
        header1,header2
        value1,value2
        value3,value4
        ''')


class Test_Reader(unittest.TestCase):

    def test_header(self):
        reader = m.Reader(h1h2v1v2())

        self.assertListEqual(
            [u'header1', u'header2'],
            reader.header)

    def test_iterate_over_input(self):
        reader = m.Reader(h1h2v1v2v3v4())

        self.assertListEqual(
            [
                [u'value1', u'value2'],
                [u'value3', u'value4']],
            list(reader))

    def test_select1(self):
        reader = m.Reader(h1h2v1v2())

        for v2, v1, v22 in reader.select([u'header2', u'header1', u'header2']):
            # executed only once - as the input has only one data row
            self.assertEqual(u'value2', v2)
            self.assertEqual(u'value1', v1)
            self.assertEqual(u'value2', v22)

    def test_select2(self):
        reader = m.Reader(h1h2v1v2v3v4())

        self.assertListEqual(
            [
                u'value2',
                u'value4'],
            list(reader.select([u'header2'])))

    def test_extract_for1(self):
        reader = m.Reader(h1h2v1v2())
        get_value_under_header2 = reader.extractor_for([u'header2'])

        for row in reader:
            # executed only once - as the input has only one data row
            self.assertListEqual([u'value1', u'value2'], row)
            self.assertEqual(u'value2', get_value_under_header2(row))

    def test_extract_for2(self):
        reader = m.Reader(h1h2v1v2())
        get_reversed_values = reader.extractor_for([u'header2', u'header1'])

        for row in reader:
            # executed only once - as the input has only one data row
            self.assertListEqual(
                [u'value1', u'value2'],
                row)

            self.assertSequenceEqual(
                [u'value2', u'value1'],
                get_reversed_values(row))

    def test_short_input_lines_are_OK(self):
        file = stringio(u'''\
            header1,header2
            value1
            value11,value2
            ''')

        self.assertListEqual(
            [
                [u'value1', u''],
                [u'value11', u'value2']],
            list(m.Reader(file)))

    def test_too_many_values_in_record_is_an_error(self):
        file = stringio(u'''\
            header1,header2
            value1,value2,value3
            ''')

        with self.assertRaises(ValueError):
            iter(m.Reader(file)).next()

    def test_select_columns_input_can_be_in_different_order(self):
        self.assertListEqual(
            [(u'value2', u'value1')],
            list(m.Reader(h1h2v1v2()).select([u'header2', u'header1'])))

    def test_extractor_for_multiple_columns(self):
        reader = m.Reader(h1h2v1v2())
        extract = reader.extractor_for(u'header1 header2 header1'.split())
        row = list(reader)[0]

        self.assertTupleEqual(
            tuple(u'header1 header2 header1'.split()),
            extract(reader.header))

        self.assertTupleEqual(
            tuple(u'value1 value2 value1'.split()),
            extract(row))

    def test_extractor_for_single_column(self):
        reader = m.Reader(h1h2v1v2())
        extract = reader.extractor_for(u'header2'.split())
        row = list(reader)[0]

        self.assertEqual(u'header2', extract(reader.header))
        self.assertEqual(u'value2', extract(row))
