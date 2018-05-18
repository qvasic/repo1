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

    actual = subprocess.check_output( [ prog, ], stdin=open( inp, 'rb' ) )
    return actual == open( exp, 'rb' ).read()

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
