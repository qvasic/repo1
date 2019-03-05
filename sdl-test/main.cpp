#include "SDL2/SDL.h"

#include <chrono>
#include <iostream>
#include <iomanip>
#include <thread>

void
show_joystick( )
{
    int joystick_count = SDL_NumJoysticks( );

    if ( SDL_NumJoysticks( ) < 1 )
    {
        std::cerr << "no joystick present in the system to show" << std::endl;
        return;
    }

    std::cout << "there are " << joystick_count << " joystick(s) present: " << std::endl;
    for ( int i = 0; i < joystick_count; ++i )
    {
        std::cout << i+1 << " " << SDL_JoystickNameForIndex( i ) << std::endl;
    }

    SDL_Joystick* joystick = SDL_JoystickOpen( 0 );

    if ( joystick == nullptr )
    {
        std::cerr << "couldn't open joystick" << std::endl;
        return;
    }

    int axes_count = SDL_JoystickNumAxes( joystick );
    std::cout << "opened joystick " << SDL_JoystickName( joystick )
              << ", it has " << axes_count << " axes" << std::endl;

    bool exit_event = false;
    for ( ; !exit_event; )
    {
        SDL_Event event;
        while ( SDL_PollEvent( &event ) )
        {
            if ( event.type == SDL_JOYBUTTONDOWN )
            {
                exit_event = true;
            }
        }

        std::cout << "\raxes: " << std::setprecision( 2 );
        for ( int i=0; i < axes_count; ++i )
        {
            std::cout << SDL_JoystickGetAxis( joystick, i ) / double( 0xefff ) << ' ';
        }
        std::cout << "      ";

        std::this_thread::sleep_for( std::chrono::milliseconds( 50 ) );
    }

    SDL_JoystickClose( joystick );
}

int
main( int, char** )
{
    if ( SDL_Init( SDL_INIT_JOYSTICK ) < 0 )
    {
        std::cout << "COULDN'T INIT SDL: " << SDL_GetError( ) << std::endl;
        return -1;
    }

    show_joystick( );

    SDL_Quit( );
}
