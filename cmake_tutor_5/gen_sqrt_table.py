from __future__ import print_function

"""gen_sqrt_table.py
generates c code with table of square roots
usage:
    gen_sqrt_table.py table_size [file_output]"""

def main():
    import sys
    import math

    if len( sys.argv ) < 2 or len( sys.argv ) > 3:
        print( __doc__ )
        return

    table_size = int( sys.argv[1] )

    if len( sys.argv ) == 3:
        out = open( sys.argv[2], 'w' )
    else:
        out = sys.stdout

    print( "double sqrt_table[] = {", file=out )
    for i in range( table_size ):
        print( "{}, ".format( math.sqrt( i ) ), file=out )
    print( "0 };", file=out )

if __name__ == '__main__':
    main()

