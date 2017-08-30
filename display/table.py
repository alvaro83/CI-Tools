from itertools import izip_longest
from display.console_colors import has_color_ok, has_color_error, del_color_ok, del_color_error, color_ok, color_error

import textwrap

class Table(object):
    def __init__(self, list_of_lists, maximum_lengths=[], spacing=False, count=False):
        """
        :param list_of_lists: table composed of rows, every row being composed by fields
                              The first row will be considered the Title, and will be
                              separated from the rest of rows with a horizontal line.
        :type list_of_lists: list[list]
        :param maximum_lengths: if specified, they impose a maximum size for the fields.
                                The tool will try to break the lines with carriage returns in
                                to accommodate to that maximum. Use value 0 to specify no maximum
        :type maximum_lengths: list[int]
        :param spacing: when True, an empty line is added betweetn every line provided by list_of_lists
        :type spacing: bool
        :param count: if True, a line is added with the total number of rows. Take into account that the
                      first row is always the Title, and therefore, it will not be counted as a row.
        :type count: bool
        """
        self.length=len(list_of_lists)-1 if count else None

        # Cut to maximum lengths if necessary
        for row in list_of_lists:
            for i, maxl in zip(range(len(row)), maximum_lengths):
                if maxl:
                    row[i]="\n".join(textwrap.wrap(str(row[i]), maxl, break_long_words=True))

        # Apply spacing
        if spacing:
            l = list_of_lists
            list_of_lists = list_of_lists[0:1]
            for lis in l[1:]:
                list_of_lists.append(lis)
                list_of_lists.append( [""]*len(lis))

        # Expand fields to break them into new rows in case they contain carriage return (\n)
        # This leads to have more rows to accommodate the extra lines
        ll=[]
        for row in list_of_lists:
            expanded_fields = [ str(field).split('\n') for field in row ]
            for row2 in izip_longest(*expanded_fields):
                ll.append( [ f or "" for f in row2] )

        # Add extra padding for the fields to separated from the vertical pipes
        self.l=[ [ ' %s ' % field for field in row] for row in ll]


    def __str__(self):
        sizes = [ [ len(field) for field in row] for row in self.l]
        max_column_sizes = [ max (fields ) for fields in zip(*sizes)]
        horizontal_separation = "+" + '+'.join('-' * max_column_size for max_column_size in max_column_sizes) + '+\n'

        ret=""
        for idx, row in enumerate(self.l):
            if idx==0:
                ret += horizontal_separation
            for field,maxsize in zip(row, max_column_sizes):
                ret += '|'
                if has_color_ok(field):
                    field = del_color_ok(field)
                    ret += color_ok(field.ljust(maxsize))
                elif has_color_error(field):
                    field = del_color_error(field)
                    ret += color_error(field.ljust(maxsize))
                else:
                    ret += field.ljust(maxsize)
            ret += '|\n'
            if idx == 0:
                ret += horizontal_separation

        ret += horizontal_separation

        if self.length is not None:
            msg_rows= " #elements: %d"  % self.length
            ret += "|" + \
                   msg_rows + ' '*(sum(max_column_size+1 for max_column_size in max_column_sizes)-1-len(msg_rows)) + \
                   '|\n'
            ret += horizontal_separation

        return ret
