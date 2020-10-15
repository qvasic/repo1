def print_permutations( possible_chars, max_level ):
    if max_level > 0 and len( possible_chars ) > 0:
        sequence = [ 0 ]
        while sequence:
            if len( sequence ) == max_level:
                print( *( possible_chars[ idx ] for idx in sequence ), sep="" )

def main( ):
    print( "perm recursive" )
    print_permutations_recursive( "123", 4, "", 0 )


if __name__ == "__main__":
    main( )
