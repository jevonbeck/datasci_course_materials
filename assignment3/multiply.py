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
    key = record[0]
    row = record[1]
    col = record[2]

    # assuming 5x5 matrices
    for x in range(5):
        if key == u'a':
            mr.emit_intermediate((row, x), record)
        elif key == u'b':
            mr.emit_intermediate((x, col), record)
        else:
            print u'Unknown matrix'


def add_to_map(map, key, val):
    if key in map:
        map[key].append(val)
    else:
        map[key] = [val]


def reducer(key, list_of_values):
    # key: word
    # value: list of occurrence counts
    mult_map = {}
    for x in list_of_values:
        matr = x[0]
        row = x[1]
        col = x[2]
        val = x[3]
        if matr == u'a':
            add_to_map(mult_map, col, val)
        elif matr == u'b':
            add_to_map(mult_map, row, val)
        else:
            print u'Unknown matrix'

    total = 0
    for x in mult_map:
        arr = mult_map[x]
        if len(arr) == 2:
            total += (arr[0] * arr[1])

    mr.emit((key[0], key[1], total))



# Do not modify below this line
# =============================
if __name__ == '__main__':
    inputdata = open(sys.argv[1])
    mr.execute(inputdata, mapper, reducer)
