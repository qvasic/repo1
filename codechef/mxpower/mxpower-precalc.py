def calculate_power( x, y, size, N, E, E_piramid_sums, E_ldiagonal_sums, E_rdiagonal_sums ):
    if size == 1:
        return E[y][x]

    sum = E_piramid_sums[y+size-1][x] - E_piramid_sums[y-1][x+size-1] - E_piramid_sums[y-1][x-size+1]
    if y - size >= 0:
        sum += E_piramid_sums[y - size][x]
    if x - size >= 0:
        sum -= E_ldiagonal_sums[y-1][x-size]
    if x + size < N:
        sum -= E_rdiagonal_sums[y-1][x+size]

    return sum


def find_most_power( N, E, E_piramid_sums, E_ldiagonal_sums, E_rdiagonal_sums ):
    largest_power = E[0][0]
    size = 1
    while True:
        start = 0 + size - 1
        end = N - size + 1
        if start >= end:
            break
        for x in range( start, end ):
            for y in range( start, end ):
                power = calculate_power( x, y, size, N, E, E_piramid_sums, E_ldiagonal_sums, E_rdiagonal_sums )
                #print( "diamond x={} y={} size={} power={}".format( x, y, size, power ) )
                if power > largest_power:
                    largest_power = power

        size += 1

    return largest_power


def run_test( ):
    N = int(input())

    if N == 1:
        print( input( ) )
        return

    E = []
    E_piramid_sums = []
    E_ldiagonal_sums = []
    E_rdiagonal_sums = []

    # first row
    E.append(tuple(int(e) for e in input().split()))
    assert (len(E[0]) == N)
    E_piramid_sums.append(E[0])
    E_ldiagonal_sums.append( E[0] )
    E_rdiagonal_sums.append( E[0] )

    # second row
    E.append(tuple(int(e) for e in input().split()))
    assert (len(E[1]) == N)

    last_row = E[-2]
    new_piramid_sums = []
    new_ldiagonal_sums = []
    new_rdiagonal_sums = []

    new_piramid_sums.append(E[-1][0] + last_row[0] + last_row[1])
    new_ldiagonal_sums.append( E[-1][0] )
    new_rdiagonal_sums.append(E[-1][0] + E_rdiagonal_sums[-1][1])

    for i in range(1, N - 1):
        new_piramid_sums.append(E[-1][i] + last_row[i - 1] + last_row[i] + last_row[i + 1])
        new_ldiagonal_sums.append( E[-1][i] + E_ldiagonal_sums[-1][i-1] )
        new_rdiagonal_sums.append( E[-1][i] + E_rdiagonal_sums[-1][i+1] )

    new_piramid_sums.append(E[-1][-1] + last_row[-2] + last_row[-1])
    new_ldiagonal_sums.append( E[-1][-1] + E_ldiagonal_sums[-1][-2] )
    new_rdiagonal_sums.append( E[-1][-1] )

    E_piramid_sums.append(new_piramid_sums)
    E_ldiagonal_sums.append( new_ldiagonal_sums )
    E_rdiagonal_sums.append(new_rdiagonal_sums)

    for n in range( 2, N ):
        E.append(tuple(int(e) for e in input().split()))
        assert (len(E[-1]) == N)

        last_row = E[-2]
        new_piramid_sums = []
        new_ldiagonal_sums = []
        new_rdiagonal_sums = []

        new_piramid_sums.append( E[-1][0] + last_row[0] + E_piramid_sums[-1][1] )
        new_ldiagonal_sums.append(E[-1][0])
        new_rdiagonal_sums.append(E[-1][0] + E_rdiagonal_sums[-1][1])

        for i in range( 1, N-1 ):
            new_piramid_sums.append( E[-1][i] + E_piramid_sums[-1][i-1] + last_row[i] + E_piramid_sums[-1][i+1] - E_piramid_sums[-2][i] )
            new_ldiagonal_sums.append(E[-1][i] + E_ldiagonal_sums[-1][i - 1])
            new_rdiagonal_sums.append(E[-1][i] + E_rdiagonal_sums[-1][i + 1])

        new_piramid_sums.append( E[-1][-1] + E_piramid_sums[-1][-2] + last_row[-1] )
        new_ldiagonal_sums.append(E[-1][-1] + E_ldiagonal_sums[-1][-2])
        new_rdiagonal_sums.append(E[-1][-1])

        E_piramid_sums.append( new_piramid_sums )
        E_ldiagonal_sums.append(new_ldiagonal_sums)
        E_rdiagonal_sums.append(new_rdiagonal_sums)

    
    #print( "E", *E, sep="\n" )
    #print( "E_piramid_sums", *E_piramid_sums, sep="\n" )
    #print("E_ldiagonal_sums", *E_ldiagonal_sums, sep="\n")
    #print("E_rdiagonal_sums", *E_rdiagonal_sums, sep="\n")
    print( find_most_power( N, E, E_piramid_sums, E_ldiagonal_sums, E_rdiagonal_sums ) )


def main():
    T = int( input( ) )
    for t in range( T ):
        run_test( )


if __name__ == "__main__":
    main()
