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

class Renderer
{
public:
    explicit Renderer( SDL_Renderer* sdl_renderer_ptr )
        : m_sdl_renderer_ptr( sdl_renderer_ptr )
    {}

    ~Renderer( )
    {
        SDL_DestroyRenderer( m_sdl_renderer_ptr );
    }


    void clear( )
    {
        SDL_RenderClear( m_sdl_renderer_ptr );
    }

    void present( )
    {
        SDL_RenderPresent( m_sdl_renderer_ptr );
    }

    void set_draw_color( Uint8 r, Uint8 g, Uint8 b, Uint8 a )
    {
        SDL_SetRenderDrawColor( m_sdl_renderer_ptr, r, g, b, a );
    }

    void draw_line( int x1, int y1, int x2, int y2 )
    {
        SDL_RenderDrawLine( m_sdl_renderer_ptr, x1, y1, x2, y2 );
    }

private:
    SDL_Renderer* m_sdl_renderer_ptr;
};

class Window
{
public:
    Window( const char *title, int x, int y, int w, int h, Uint32 flags )
        : m_sdl_window_ptr( SDL_CreateWindow( title, x, y, w, h, flags ) )
    {
        if ( m_sdl_window_ptr == nullptr )
        {
            throw std::runtime_error( std::string( "Could not create SDL window: " ) + SDL_GetError( ) );
        }
    }





    SDL_Surface* get_surface( )
    {
        return SDL_GetWindowSurface( m_sdl_window_ptr );
    }

    void update_window_surface( )
    {
        SDL_UpdateWindowSurface( m_sdl_window_ptr );
    }

    Renderer create_accelerated_renderer( )
    {
        auto* sdl_renderer_ptr = SDL_CreateRenderer( m_sdl_window_ptr, -1, SDL_RENDERER_ACCELERATED );
        if ( sdl_renderer_ptr == nullptr )
        {
            throw std::runtime_error( std::string( "Could not create SDL renderer: " ) + SDL_GetError( ) );
        }
        return Renderer( sdl_renderer_ptr );
    }



    ~Window()
    {
        SDL_DestroyWindow( m_sdl_window_ptr );
    }

private:
    SDL_Window* m_sdl_window_ptr;
};

}

extern "C" int
SDL_main( int, char** )
try
{
    sdl::Library library( SDL_INIT_VIDEO );
    sdl::Window window( "sdl-test2", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                        800, 600, 0 );

    auto renderer = window.create_accelerated_renderer( );

    SDL_Event event;
    bool quit = false;
    bool redraw = false;

    int x = 0, y = 0;

    for ( ;; )
    {
        redraw = false;

        while ( SDL_PollEvent( &event ) )
        {
            if ( event.type == SDL_QUIT )
            {
                quit = true;
            }
            else if ( event.type = SDL_MOUSEMOTION )
            {
                x = event.motion.x;
                y = event.motion.y;
                redraw = true;
            }
        }

        if ( quit )
        {
            break;
        }

        if ( redraw )
        {
            renderer.set_draw_color( 255, 255, 255, SDL_ALPHA_OPAQUE );
            renderer.clear( );
            renderer.set_draw_color( 0, 0, 0, SDL_ALPHA_OPAQUE );
            renderer.draw_line( 0, 0, x, y );
            renderer.present( );
        }
        else
        {
            std::this_thread::sleep_for( std::chrono::milliseconds( 30 ) );
        }
    }

    return 0;
}
catch( const std::exception& e)
{
    std::cerr << "EXCEPTION IN MAIN: " << e.what( ) << std::endl;
    return 1;
}
