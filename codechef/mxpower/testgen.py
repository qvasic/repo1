def generate_worst_case_scenario( N = 100, minmax_power = 9 ):
    from random import randint
    minmax = 10 ** minmax_power

    print( N )
    for n in range( N ):
        print( *( randint( -minmax, minmax ) for i in range( N ) ) )


if __name__ == "__main__":
    import sys
    if len( sys.argv ) > 1 and sys.argv[1] == "max":
        T = 100
        print( T )
        for i in range( T ):
            generate_worst_case_scenario( 100 )
    else:
        T = 10
        print( T )
        for i in range( 1, T+1 ):
            generate_worst_case_scenario( i, 1 )
