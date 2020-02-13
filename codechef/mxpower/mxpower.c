#include <stdio.h>

#define N_MAX 100

typedef long long int Integer;

int N;
Integer E[N_MAX][N_MAX];
Integer E_piramid_sum[N_MAX][N_MAX];
Integer E_left_diagonal_sum[N_MAX][N_MAX];
Integer E_right_diagonal_sum[N_MAX][N_MAX];

void read_and_precalculate_test_case( )
{
    scanf( "%d", &N );

    if ( N == 1 )
    {
        scanf( "%lld", &E[0][0] );
        return;
    }

    // first row
    for( int x=0; x < N; ++x )
    {
        scanf( "%lld", &E[0][x] );
        E_piramid_sum[0][x] = E_left_diagonal_sum[0][x] = E_right_diagonal_sum[0][x] = E[0][x];
    }

    // second row
    scanf( "%lld", &E[1][0] );
    E_piramid_sum[1][0] = E[1][0] + E[0][0] + E[0][1];
    E_left_diagonal_sum[1][0] = E[1][0];
    E_right_diagonal_sum[1][0] = E[1][0] + E_right_diagonal_sum[0][1];

    for( int x=1; x < N-1; ++x )
    {
        scanf( "%lld", &E[1][x] );
        E_piramid_sum[1][x] = E[1][x] + E[0][x-1] + E[0][x] + E[0][x+1];
        E_left_diagonal_sum[1][x] = E[1][x] + E_left_diagonal_sum[0][x-1];
        E_right_diagonal_sum[1][x] = E[1][x] + E_right_diagonal_sum[0][x+1];
    }

    scanf( "%lld", &E[1][N-1] );
    E_piramid_sum[1][N-1] = E[1][N-1] + E[0][N-1] + E[0][N-2];
    E_left_diagonal_sum[1][N-1] = E[1][N-1] + E_left_diagonal_sum[0][N-2];
    E_right_diagonal_sum[1][N-1] = E[1][N-1];

    // rest of the rows
    for( int y=2; y < N; ++y )
    {
        scanf( "%lld", &E[y][0] );
        E_piramid_sum[y][0] = E[y][0] + E[y-1][0] + E_piramid_sum[y-1][1];
        E_left_diagonal_sum[y][0] = E[y][0];
        E_right_diagonal_sum[y][0] = E[y][0] + E_right_diagonal_sum[y-1][1];

        for( int x=1; x < N-1; ++x )
        {
            scanf( "%lld", &E[y][x] );
            E_piramid_sum[y][x] = E[y][x] + E[y-1][x] + E_piramid_sum[y-1][x-1] + E_piramid_sum[y-1][x+1] - E_piramid_sum[y-2][x];
            E_left_diagonal_sum[y][x] = E[y][x] + E_left_diagonal_sum[y-1][x-1];
            E_right_diagonal_sum[y][x] = E[y][x] + E_right_diagonal_sum[y-1][x+1];
        }

        scanf( "%lld", &E[y][N-1] );
        E_piramid_sum[y][N-1] = E[y][N-1] + E[y-1][N-1] + E_piramid_sum[y-1][N-2];
        E_left_diagonal_sum[y][N-1] = E[y][N-1] + E_left_diagonal_sum[y-1][N-2];
        E_right_diagonal_sum[y][N-1] = E[y][N-1];
    }
}

Integer calculate_diamond_power( int x, int y, int size )
{
    if ( size == 1 )
    {
        return E[y][x];
    }

    Integer power = E_piramid_sum[y+size-1][x] - E_piramid_sum[y-1][x+size-1] - E_piramid_sum[y-1][x-size+1];

    if ( y - size >= 0 )
    {
        power += E_piramid_sum[y - size][x];
    }

    if ( x - size >= 0 )
    {
        power -= E_left_diagonal_sum[y-1][x-size];
    }

    if ( x + size < N )
    {
        power -= E_right_diagonal_sum[y-1][x+size];
    }

    return power;
}

Integer find_most_power( )
{
    Integer most_power = E[0][0];
    int size = 1;
    for ( ;; )
    {
        int start = 0 + size - 1;
        int end = N - size + 1;
        if ( end <= start )
        {
            break;
        }
        for ( int y = start; y < end; ++y )
        {
            for ( int x = start; x < end; ++x )
            {
                Integer power = calculate_diamond_power( x, y, size );
                // printf( "diamond, x=%d, y=%d, size=%d, power=%lld\n", x, y, size, power );
                if ( power > most_power )
                {
                    most_power = power;
                }
            }
        }
        ++size;
    }
    return most_power;
}

Integer do_test_case( )
{
    read_and_precalculate_test_case( );

    if ( N == 1 )
    {
        return E[0][0];
    }

	return find_most_power( );
}

int main( )
{
	int t, T;
	scanf( "%d", &T );
	for( t = 0; t < T; ++t )
	{
		printf( "%lld\n", do_test_case( ) );
	}
}