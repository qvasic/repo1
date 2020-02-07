def generate_worst_case_scenario( ):
    from random import randint
    N = 100
    minmax = 10 ** 9

    print( N )
    for n in range( N ):
        print( *( randint( -minmax, minmax ) for i in range( N ) ) )


if __name__ == "__main__":
    print( 1 )
    generate_worst_case_scenario()