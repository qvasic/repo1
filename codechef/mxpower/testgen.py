def generate_worst_case_scenario( N = 100, minmax_power = 9 ):
    from random import randint
    minmax = 10 ** minmax_power

    print( N )
    for n in range( N ):
        print( *( randint( -minmax, minmax ) for i in range( N ) ) )


if __name__ == "__main__":
    import sys
    print( 20 )
    for i in range( 1, 11 ):
        generate_worst_case_scenario( i, 1 )
        generate_worst_case_scenario( i, 1 )
