def run_test( ):
    N = int(input())

    if N == 1:
        print( input( ) )
        return

    E = []
    E_sums = []

    # first row
    E.append(tuple(int(e) for e in input().split()))
    assert (len(E[0]) == N)
    E_sums.append(E[0])

    # second row
    E.append(tuple(int(e) for e in input().split()))
    assert (len(E[1]) == N)

    last_row = E[-2]
    new_sums = []
    new_sums.append(E[-1][0] + last_row[0] + last_row[1])
    for i in range(1, N - 1):
        new_sums.append(E[-1][i] + last_row[i - 1] + last_row[i] + last_row[i + 1])
    new_sums.append(E[-1][-1] + last_row[-2] + last_row[-1])
    E_sums.append(new_sums)

    for n in range( 2, N ):
        E.append(tuple(int(e) for e in input().split()))
        assert (len(E[-1]) == N)

        new_sums = []
        last_row = E[-2]
        new_sums = []
        new_sums.append( E[-1][0] + last_row[0] + E_sums[-1][1] )
        for i in range( 1, N-1 ):
            new_sums.append( E[-1][i] + E_sums[-1][i-1] + last_row[i] + E_sums[-1][i+1] - E_sums[-2][i] )
        new_sums.append( E[-1][-1] + E_sums[-1][-2] + last_row[-1] )
        E_sums.append( new_sums )

    print( "E", *E, sep="\n" )
    print( "E_sums", *E_sums, sep="\n" )

def main():
    T = int( input( ) )
    for t in range( T ):
        run_test( )

if __name__ == "__main__":
    main()
