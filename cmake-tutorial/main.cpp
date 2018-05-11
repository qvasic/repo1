#include <cstdio>
#include <cmath>

#include "cmake-tutorial-config.h"
#include "my_meth_lab.h"

int main(int argc, char *argv[])
{
    do_meth();
    std::printf( "sqroot ver%d.%d\n", cmake_tutorial_VERMAJ, cmake_tutorial_VERMIN );

    double n;

    while( std::scanf( "%lf", &n ) == 1 )
    {
        std::printf( "%lf\n", std::sqrt( n ) );
    }

    return 0;
}
