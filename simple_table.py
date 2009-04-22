try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class SimpleTable(object):

    def __init__(self, data=None, headers=None, first_row_headers=False):
        self.data = data
        self.headers = headers
        self.first_row_headers = first_row_headers

    def __str__(self):
        if self.first_row_headers and not self.headers:
            self.headers = self.data.pop(0)

        return self.format_table()

    def format_table(self, padding=10):
        out_buffer = StringIO()
        column_widths = self.get_column_widths()

        if self.headers:
            out_buffer.write(self.format_headers(column_widths, padding))

        for row in self.data:
            for i, column in enumerate(row):
                col_width = column_widths[i] + padding
                out_buffer.write(str(column).ljust(col_width))

            out_buffer.write('\n')

        return out_buffer.getvalue()

    def get_column_widths(self):
        """Gets a tuple of the maximum column lengths in a dataset."""
        maxlen = 0
        for row in self.data:
            maxlen = max(maxlen, len(row))

        widths = [0 for _ in range(maxlen)]

        for row in self.data:
            for i, column in enumerate(row):
                widths[i] = max(widths[i], len(str(column)))

        return tuple(widths)

    def format_headers(self, column_widths, padding=10):
        out_buffer = StringIO()
        table_width = sum(column_widths) + (padding * len(column_widths))

        for i, header in enumerate(self.headers):
            col_width = column_widths[i] + padding
            out_buffer.write(str(header).ljust(col_width))

        out_buffer.write('\n')
        out_buffer.write('-' * table_width)
        out_buffer.write('\n')

        return out_buffer.getvalue()
