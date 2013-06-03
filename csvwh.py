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
            # pad missing input with empty values
            row_length = len(row)
            if row_length == header_length:
                pass
            elif row_length < header_length:
                row += (unicode(),) * (header_length - row_length)
            else:
                raise ValueError(
                    'Invalid CSV - line {} has more values than the header'
                    .format(self.reader.line_num))
            yield row

    def select(self, columns):
        '''I read the CSV file, but return only the requested columns.

        I am an iterator yielding records.
        '''
        header_indices = [self.header.index(column) for column in columns]
        extractor = operator.itemgetter(*header_indices)
        return (extractor(row) for row in self)
