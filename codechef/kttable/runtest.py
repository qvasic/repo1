"""runtest.py

runs a test on stdin/stdout
convenience utility for running tests in cmake

1st arg - program to be tested
2nd arg - file with data to be sent into stdin
3rd arg - expected output from stdout

returns 0 if output is equal to expected
returns 1 if not
"""

def run_test( prog, inp, exp ):
    """run program prog, feed file inp into its stdin, compare its stdout with file exp"""
    import subprocess

    actual = subprocess.check_output( [ prog, ], stdin=open( inp, 'r' ) ).decode().splitlines()
    expect = open( exp, 'r' ).read().splitlines()

    if len( actual ) != len( expect ):
        print( 'line count differs' )
        return False
    else:
        for line_num, ( actual_line, expect_line ) in enumerate( zip( actual, expect ) ):
            if actual_line != expect_line:
                print( 'lines number {} differ, actual: {}, expected: {}'.format(
                                                             line_num+1, repr(actual_line),
                                                             repr(expect_line) ) )
                return False
        else:
            return True

def main():
    import sys

    if len( sys.argv ) != 4:
        print( __doc__ )
        sys.exit( 1 )
    else:
        if run_test( sys.argv[1], sys.argv[2], sys.argv[3] ):
            print( __file__, ": test passed" )
            sys.exit( 0 )
        else:
            print( __file__, ": test failed" )
            sys.exit( 1 )

if __name__ == '__main__':
    main()
