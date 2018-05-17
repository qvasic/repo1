"""
runs a test
1st arg - program to be tested
2nd arg - file with data to be sent into stdin
3rd arg - expected output from stdout
4th arg - CMake executable to be used for comparison

return 0 if output is equal to expected
return 1 if not
"""

def main():
    print( __name__, "main()" )
    print( __doc__ )

if __name__ == '__main__':
    main()
