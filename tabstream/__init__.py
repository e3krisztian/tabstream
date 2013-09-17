import operator
import functools
import inspect


__version__ = (0, 1, 0, 'dev', 0)


def stream_filter(function):
    @functools.wraps(function)
    def stream_filter(stream):
        return function(iter(stream))
    return stream_filter


@stream_filter
def pad(stream):
    '''I am a filter, I pad short rows to match header length'''
    header = stream.next()
    yield header

    header_length = len(header)
    for row in stream:
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


def select(stream, column_names):
    '''I process a record stream with a header row,
    returning only the requested columns.

    I am an iterator yielding records.

    NOTE: I am not a filter, use me in application for loops.
    '''
    def _select(stream, column_names):
        header = stream.next()
        header_indices = [header.index(column) for column in column_names]
        extract = operator.itemgetter(*header_indices)

        return (extract(row) for row in stream)

    return _select(iter(stream), column_names)


def _fields_extractor(header, fields):
    if len(fields) == 0:
        def get_fields(__):
            return ()
    elif len(fields) == 1:
        _get_fields = operator.itemgetter(header.index(fields[0]))

        def get_fields(row):
            return (_get_fields(row),)
    else:
        get_fields = operator.itemgetter(
            *[header.index(field) for field in fields])

    return get_fields


def make_field_adder(output_field, function, input_fields):
    '''I create a stream filter that adds a new field to the stream.

    The new field will have the name `output_field` and its values
    will be calculated by `function(*input_fields)`
    '''
    @stream_filter
    @functools.wraps(function)
    def filter(stream):
        header = stream.next()
        # header
        yield tuple(header) + (output_field,)

        get_fields = _fields_extractor(header, input_fields)

        # data
        for row in stream:
            yield tuple(row) + (function(*get_fields(row)),)

    return filter


def add_field(function):
    '''I am a function decorator, I make a stream filter from the function
    specified by its signature to add a new field to the stream.

    The function name is to be `add_`<output_field>,
    its parameter names are matched with the stream fields with the same name.
    '''
    assert function.__name__.startswith('add_')
    output_field = function.__name__[len('add_'):]

    argspec = inspect.getargspec(function)
    input_fields = argspec.args

    return make_field_adder(output_field, function, input_fields)


def delete_fields(*fields_to_delete):
    '''I make a filter on tabular stream that removes fields from the stream
    '''
    @stream_filter
    def delete_fields(stream):
        header = stream.next()
        output_header = tuple(
            field for field in header if field not in fields_to_delete)

        get_fields = _fields_extractor(header, output_header)

        yield get_fields(header)
        for row in stream:
            yield get_fields(row)

    return delete_fields
