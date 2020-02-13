#include <stdio.h>

#define N_MAX 100

typedef long long int Integer;

Integer E[N_MAX][N_MAX];
Integer E_piramid_sum[N_MAX][N_MAX];
Integer E_left_diagonal_sum[N_MAX][N_MAX];
Integer E_right_diagonal_sum[N_MAX][N_MAX];

Integer do_test_case( )
{
	int N;
	scanf( "%d", &N );

    if ( N == 1 )
    {
        scanf( "%lld", &E[0][0] );
        return E[0][0];
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

	return -1;
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