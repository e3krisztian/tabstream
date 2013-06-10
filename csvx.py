import unicodecsv
import operator


class Reader(object):

    '''I am the Reader of CSV streams with header.
    '''

    def __init__(self, *args, **kwargs):
        self.reader = iter(unicodecsv.reader(*args, **kwargs))
        self.header = self.reader.next()

    def __iter__(self):
        '''I am reading the records in the CSV file one-by-one.

        I ensure that every record has exactly the same number of fields
        as the header.
        '''
        header_length = len(self.header)
        for row in self.reader:

            # FIXME: padding stuff looks like a separate feature!

            # pad missing input with empty values
            row_length = len(row)
            if row_length == header_length:
                pass
            elif row_length < header_length:
                row += [unicode()] * (header_length - row_length)
            else:
                raise ValueError(
                    'Invalid CSV - line {} has more values than the header'
                    .format(self.reader.line_num))

            yield row

    def select(self, columns):
        '''I read the CSV file, but return only the requested columns.

        I am an iterator yielding records.
        '''
        extract = self.extractor_for(columns)
        return (extract(row) for row in self)

    def extractor_for(self, columns):
        '''I create a function that extracts the given columns from a row.

        The returned function will return a tuple of column values
        if there are more than one columns,
        or the single value if columns has one element.
        '''
        header_indices = [self.header.index(column) for column in columns]
        return operator.itemgetter(*header_indices)
