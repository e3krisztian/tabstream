import operator
import io


__version__ = (0, 1, 0, 'dev', 0)


def fix_missing_columns(seq_stream):
    iseq_stream = iter(seq_stream)
    header = iseq_stream.next()
    yield header

    header_length = len(header)
    for row in iseq_stream:
        # pad missing input with empty values
        row_length = len(row)
        if row_length == header_length:
            yield row
        elif row_length < header_length:
            yield row + row.__class__([u''] * (header_length - row_length))
        else:
            raise ValueError(
                'Invalid CSV - line {} has more values than the header'
                .format(row))


def select(seq_stream, column_names):
    '''I process a CSV record stream with a header,
    but return only the requested columns.

    I am an iterator yielding records.
    '''
    iseq_stream = iter(seq_stream)
    header = iseq_stream.next()
    header_indices = [header.index(column) for column in column_names]
    extract = operator.itemgetter(*header_indices)

    return (extract(row) for row in iseq_stream)


def selectx(csv_external, column_names):
    '''I process a CSV external with a header,
    but return only the requested columns.

    I am an iterator yielding records.
    '''
    import unicodecsv
    with csv_external.readable_stream() as stream:
        reader = unicodecsv.reader(io.TextIOWrapper(stream))
        for row in select(reader, column_names):
            yield row


import functools
# import operator
import inspect


def make_field_adder(output_field, function, input_fields):

    def _fields_extractor(header):
        if len(input_fields) == 0:
            def get_fields(__):
                return ()
        elif len(input_fields) == 1:
            _get_fields = operator.itemgetter(header.index(input_fields[0]))

            def get_fields(row):
                return (_get_fields(row),)
        else:
            get_fields = operator.itemgetter(
                *[header.index(field) for field in input_fields])
        return get_fields

    def _filter(stream):
        header = stream.next()
        # header
        yield tuple(header) + (output_field,)

        get_fields = _fields_extractor(header)

        # data
        for row in stream:
            yield tuple(row) + (function(*get_fields(row)),)

    @functools.wraps(function)
    def filter(stream_with_header):
        return _filter(iter(stream_with_header))

    return filter


def add_field(function):
    assert function.__name__.startswith('add_')
    output_field = function.__name__[len('add_'):]

    argspec = inspect.getargspec(function)
    input_fields = argspec.args

    return make_field_adder(output_field, function, input_fields)
