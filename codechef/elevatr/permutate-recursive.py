def print_permutations_recursive( possible_chars, max_level, chars, level ):
    if level >= max_level:
        print( chars )
        return
    
    for char in possible_chars:
        print_permutations_recursive( possible_chars, max_level, chars + char, level+1 )

def main( ):
    print( "perm recursive" )
    print_permutations_recursive( "123", 4, "", 0 )


if __name__ == "__main__":
    main( )
