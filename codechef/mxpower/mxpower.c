#include <stdio.h>

#define N_MAX 100

typedef long long int Integer;

Integer E[N_MAX][N_MAX];
Integer E_piramid_sum[N_MAX][N_MAX];
Integer E_left_diagonal_sum[N_MAX][N_MAX];
Integer E_right_diagonal_sum[N_MAX][N_MAX];

void do_test_case( )
{
	int n, N;
	scanf( "%d", &N );

	for( n=0; n < N; ++n )
	{
		scanf( "%lld", &E[0][n] );
	}

	for( n=0; n < N; ++ n )
	{
		printf( "%lld ", E[0][n] );
	}
	printf( "\n" );
}

int main( )
{
	int t, T;
	scanf( "%d", &T );
	for( t = 0; t < T; ++t )
	{
		do_test_case( );
	}
}