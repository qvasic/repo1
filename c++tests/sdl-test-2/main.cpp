#include <SDL2/SDL.h>
#include <iostream>
#include <exception>

namespace sdl
{

void
create_window( )
{

    std::cout << "SDL window created, now closing it." << std::endl;


}

class Library
{
public:
    Library( Uint32 flags )
    {
        if ( SDL_Init( flags ) != 0 )
        {
            throw std::runtime_error( std::string( "Could not initialize SDL video system: " ) + SDL_GetError( ) );
        }
    }
    ~Library()
    {
        SDL_Quit( );
    }
};

class Window
{
public:
    Window( const char *title, int x, int y, int w, int h, Uint32 flags )
        : m_sdl_window( SDL_CreateWindow( title, x, y, w, h, flags ) )
    {
        if ( m_sdl_window == nullptr )
        {
            throw std::runtime_error( std::string( "Could not create SDL window: " ) + SDL_GetError( ) );
        }
    }

    ~Window()
    {
        SDL_DestroyWindow( m_sdl_window );
    }

private:
    SDL_Window* m_sdl_window;
};

}

extern "C" int
SDL_main( int, char** )
try
{
    sdl::Library lib( SDL_INIT_VIDEO );
    sdl::Window wnd( "asdfasdf", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                     800, 600, 0 );
    return 0;
}
catch( const std::exception& e)
{
    std::cerr << "EXCEPTION IN MAIN: " << e.what( ) << std::endl;
    return 1;
}
