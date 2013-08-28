import operator
import unicodecsv
import io


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
    with csv_external.readable_stream() as stream:
        reader = unicodecsv.reader(io.TextIOWrapper(stream))
        for row in select(reader, column_names):
            yield row
