#include <SDL2/SDL.h>
#include <iostream>
#include <exception>
#include <chrono>
#include <thread>

namespace sdl
{

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

    SDL_Surface* get_surface( )
    {
        return SDL_GetWindowSurface( m_sdl_window );
    }

    void update_window_surface( )
    {
        SDL_UpdateWindowSurface( m_sdl_window);
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
    sdl::Window wnd( "sdl-test2", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                     800, 600, 0 );

    auto* surface = wnd.get_surface( );
    SDL_Rect rect{ 10, 10, 200, 100 };
    SDL_FillRect( surface, &rect, SDL_MapRGB( surface->format, 128, 64, 0 ) );
    SDL_FreeSurface( surface );
    wnd.update_window_surface( );


    SDL_Event event;
    bool quit = false;

    for ( ;; )
    {

        while ( SDL_PollEvent( &event ) )
        {
            if ( event.type == SDL_QUIT )
            {
                quit = true;
            }
        }

        std::this_thread::sleep_for( std::chrono::milliseconds( 30 ) );

        if ( quit )
        {
            break;
        }
    }

    return 0;
}
catch( const std::exception& e)
{
    std::cerr << "EXCEPTION IN MAIN: " << e.what( ) << std::endl;
    return 1;
}
