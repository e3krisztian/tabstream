import operator
import functools
import inspect


__version__ = (0, 1, 0, 'dev', 0)


def stream_filter(function):
    @functools.wraps(function)
    def stream_filter(stream):
        istream = iter(stream)
        header = istream.next()
        return function(header, istream)
    return stream_filter


@stream_filter
def pad(header, stream):
    '''I am a filter, I pad short rows to match header length'''

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


def _fields_extractor_for(indices):
    if len(indices) == 0:
        # special case: no column selected
        def get_fields(__):
            return ()
        return get_fields

    if len(indices) == 1:
        # special case: one column selected
        _get_fields = operator.itemgetter(indices[0])

        def get_fields(row):
            return (_get_fields(row),)
        return get_fields

    return operator.itemgetter(*indices)


def _fields_extractor_by_names(header, fields):
    indices = [header.index(field) for field in fields]
    return _fields_extractor_for(indices)


def make_field_adder(output_field, function, input_fields):
    '''I create a stream filter that adds a new field to the stream.

    The new field will have the name `output_field` and its values
    will be calculated by `function(*input_fields)`
    '''
    @stream_filter
    @functools.wraps(function)
    def filter(header, stream):
        yield tuple(header) + (output_field,)

        get_fields = _fields_extractor_by_names(header, input_fields)
        for row in stream:
            yield tuple(row) + (function(*get_fields(row)),)

    return filter


def field_adder(function):
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
    def delete_fields(header, stream):
        output_header = tuple(
            field for field in header if field not in fields_to_delete)

        get_fields = _fields_extractor_by_names(header, output_header)

        yield get_fields(header)
        for row in stream:
            yield get_fields(row)

    return delete_fields


def rename(new_to_old_dict=None, **new_to_old_kw):
    '''I create a filter that relabels columns.

    Actually there is more, as it is possible to
    - duplicate columns
    - overwrite other rows
    '''
    new_to_old = new_to_old_dict or new_to_old_kw

    def _get_label_index_seq(header):
        old_header = {label: i for i, label in enumerate(header)}
        new_header = {}
        for (new, old) in new_to_old.iteritems():
            assert old in header, old
            index = header.index(old)
            if old in old_header:
                del old_header[old]
            new_header[new] = index

        # overwrite old_headers with new
        old_header.update(new_header)
        return old_header.items()

    def _get_sorted_label_index_seq(header):
        label_index_seq = _get_label_index_seq(header)

        def sort_key(label_index):
            label, index = label_index
            return (index, label not in header, label)

        return sorted(label_index_seq, key=sort_key)

    @stream_filter
    def rename(header, stream):
        label_index_seq = _get_sorted_label_index_seq(header)

        output_header = tuple(label for (label, __) in label_index_seq)
        output_indices = [index for (__, index) in label_index_seq]

        yield output_header

        get_fields = _fields_extractor_for(output_indices)
        for row in stream:
            yield get_fields(row)

    return rename


def add_row_number(field):
    '''I am creating a filter that will add row numbers to the stream'''
    @stream_filter
    def add_row_number(header, stream):
        yield (field,) + tuple(header)

        for index, row in enumerate(stream):
            yield (index + 1,) + tuple(row)

    return add_row_number


def pipe(*filters):
    '''I compose filters
    '''
    def pipe(stream):
        for filter in filters:
            stream = filter(stream)
        return stream
    return pipe
