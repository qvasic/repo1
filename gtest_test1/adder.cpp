#include <cstdio>

int adder( int l, int r )
{
    return l+r;
}

int main()
{
    int l, r;
    while( scanf( "%d %d\n", &l, &r ) == 2 )
        printf( "%d\n", l+r );
}
