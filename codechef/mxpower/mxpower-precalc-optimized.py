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

MAX_N = 100
E = [ [0] * MAX_N for i in range( MAX_N ) ]
E_piramid_sums = [ [0] * MAX_N for i in range( MAX_N ) ]
E_ldiagonal_sums = [ [0] * MAX_N for i in range( MAX_N ) ]
E_rdiagonal_sums = [ [0] * MAX_N for i in range( MAX_N ) ]

def run_test( ):
    N = int(input())

    if N == 1:
        print( input( ) )
        return

    # first row
    for i, e in zip( range(MAX_N), ( int(e_str) for e_str in input().split() ) ):
        E[0][i] = E_piramid_sums[0][i] = E_ldiagonal_sums[0][i] = E_rdiagonal_sums[0][i] = e

    # second row
    for i, e in zip(range(MAX_N), (int(e_str) for e_str in input().split())):
        E[1][i] = e

    E_piramid_sums[1][0] = E[1][0] + E[0][0] + E[0][1]
    E_ldiagonal_sums[1][0] = E[-1][0]
    E_rdiagonal_sums[1][0] = E[-1][0] + E_rdiagonal_sums[-1][1]

    for i in range(1, N - 1):
        E_piramid_sums[1][i] = E[1][i] + E[0][i - 1] + E[0][i] + E[0][i + 1]
        E_ldiagonal_sums[1][i] = E[1][i] + E_ldiagonal_sums[0][i-1]
        E_rdiagonal_sums[1][i] = E[1][i] + E_rdiagonal_sums[0][i+1]

    E_piramid_sums[1][N-1] = E[1][N-1] + E[0][N-2] + E[0][N-1]
    E_ldiagonal_sums[1][N-1] = E[-1][-1] + E_ldiagonal_sums[-1][-2]
    E_rdiagonal_sums[1][N-1] = E[-1][-1]

    # rest of the rows
    for n in range( 2, N ):
        for i, e in zip(range(MAX_N), (int(e_str) for e_str in input().split())):
            E[n][i] = e

        E_piramid_sums[n][0] = E[n][0] + E[n-1][0] + E_piramid_sums[n-1][1]
        E_ldiagonal_sums[n][0] = E[n][0]
        E_rdiagonal_sums[n][0] = E[n][0] + E_rdiagonal_sums[n-1][1]

        for i in range( 1, N-1 ):
            E_piramid_sums[n][i] = E[n][i] + E_piramid_sums[n-1][i-1] + E[n-1][i] + E_piramid_sums[n-1][i+1] - E_piramid_sums[n-2][i]
            E_ldiagonal_sums[n][i] = E[n][i] + E_ldiagonal_sums[n-1][i - 1]
            E_rdiagonal_sums[n][i] = E[n][i] + E_rdiagonal_sums[n-1][i + 1]

        E_piramid_sums[n][N-1] = E[n][N-1] + E_piramid_sums[n-1][N-2] + E[n-1][N-1]
        E_ldiagonal_sums[n][N-1] = E[n][N-1] + E_ldiagonal_sums[n-1][N-2]
        E_rdiagonal_sums[n][N-1] = E[n][N-1]

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
