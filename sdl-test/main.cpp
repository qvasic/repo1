#include "SDL2/SDL.h"

#include <chrono>
#include <iostream>
#include <thread>

int
main( int, char** )
{
    SDL_Init( SDL_INIT_JOYSTICK );

    std::cout << __FILE__ << std::endl;
    std::this_thread::sleep_for( std::chrono::seconds( 1 ) );
    printf( "the system has %d joysticks present\n", SDL_NumJoysticks( ) );

    SDL_Quit( );
}
