#include <iostream>

#include "func.h"

namespace
{

int somef1( int )
{
    std::cout << __func__ << std::endl;
    return 0;
}

int somef2( int )
{
    std::cout << __func__ << std::endl;
    return 0;
}

}

int main()
{
    q::func< int, int > fi1;
    q::func< int, int > fi2( somef1 );
    q::func< int, int > fi3( somef2 );

    fi2( 10 );
    fi3( 30 );

    q::func< char, char > fv;

    std::cout << "hello" << std::endl;
}

