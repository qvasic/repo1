#include <iostream>
#include "lib.h"

int main( int, char** )
{
	for( ;; )
	{
		int a, b;
		std::cin >> a >> b;
		if ( !std::cin )
		{
			break;
		}
		std::cout << lib::sum( a, b ) << std::endl;
	}
}