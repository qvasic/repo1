#include <SDL2/SDL.h>
#include <iostream>
#include <exception>

int main()
try
{
    std::cout << "one" << std::endl;
    if ( SDL_Init( SDL_INIT_VIDEO ) != 0 )
    {
        std::cout << "two" << std::endl;
        throw std::runtime_error( std::string( "Could not initialize SDL video system: " ) + SDL_GetError( ) );
    }

    std::cout << "thee" << std::endl;
    SDL_Quit( );
    std::cout << "four" << std::endl;
    return 0;
}
catch( const std::exception& e)
{
    std::cerr << "EXCEPTION IN MAIN: " << e.what( ) << std::endl;
    return 1;
}
