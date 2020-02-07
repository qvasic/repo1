example = [ [  10,   5, -10,  3 ],
            [   8,   7,  11,  2 ],
            [   1,   6, -80, 33 ],
            [  14,  13,  77, 666] ]


def iterate_diamond( E, x, y, size ):
    """
    Iterate elements in E which lie in the diamond with center x,y and size size.
    Order from top to bottom, from left to right - from lowest indexes to highest.
    """
    for i in range( size ):
        row = y - size + 1 + i
        for j in range( x-i, x+i+1 ):
            yield E[row][j]

    for i in range( 1, size ):
        row = y + i
        spread = size - i - 1
        for j in range( x-spread, x+spread+1 ):
            yield E[row][j]


def calculate_diamond_power( E, x, y, size ):
    """
    Calculates sum of all elements in the diamond.
    :param E: matrix (indexable of indexables) with values for each cell
    :param x: x-position of the center of the diamond
    :param y: y-position of the center of the diamond
    :param size: size of the diamond
    :return: summ of all the cells in E that belong to that diamond
    For instance:
    Y axis
    |
    V  X-axis -> 0   1   2
    0   E: [ [  10   5 -10 ]
    1        [   8   7  11 ]
    2        [   1   6 -80 ] ]
    If x,y,size = 0,0,1 then the result is 10, because the only element that lies inside given diamond is the first one
    of the first element of E.
    If x,y,size = 1,1,2 then result is 7 (the center) + 5 (top) + 11 (right) + 6 (bottom) + 8 (left) = 37.
    And so on."""
    result = 0
    for i in iterate_diamond( E, x, y, size ):
        result += i
    return result


def find_most_powerful_figure( E ):
    largest_power = E[0][0]
    N = len( E )
    size = 1
    while True:
        start = 0 + size - 1
        end = N - size + 1
        if start >= end:
            break
        for x in range( start, end ):
            for y in range( start, end ):
                power = calculate_diamond_power( E, x, y, size )
                if power > largest_power:
                    largest_power = power

        size += 1

    return largest_power


def main():
    T = int( input( ) )
    for t in range( T ):
        N = int( input( ) )
        E = []
        for n in range( N ):
            E.append( [ int( e ) for e in input( ).split( ) ] )
            assert( len( E[-1] ) == N )

        print( find_most_powerful_figure( E ) )

if __name__ == "__main__":
    main()
