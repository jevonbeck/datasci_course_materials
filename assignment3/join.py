import MapReduce
import sys

"""
Word Count Example in the Simple Python MapReduce Framework
"""

mr = MapReduce.MapReduce()

# =============================
# Do not modify above this line

def mapper(record):
    # key: document identifier
    # value: document contents
    key = record[1]
    value = record
    mr.emit_intermediate(key, value)

def reducer(key, list_of_values):
    # key: word
    # value: list of occurrence counts
    order = []
    line_items = []
    for x in list_of_values:
        if x[0] == u'order':
            order.append(x)
        elif x[0] == u'line_item':
            line_items.append(x)
        else:
            print u'Unknown table - ' + unicode(x[0])

    for x in order:
        for y in line_items:
            mr.emit(x + y)

# Do not modify below this line
# =============================
if __name__ == '__main__':
    inputdata = open(sys.argv[1])
    mr.execute(inputdata, mapper, reducer)
