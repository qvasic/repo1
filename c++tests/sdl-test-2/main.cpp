#include <SDL2/SDL.h>
#include <iostream>
#include <exception>
#include <chrono>
#include <thread>
#include <vector>

#include <cassert>
#include <cmath>

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

    void draw_line( int x1, int y1, int x2, int y2 ) const
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


std::vector< std::pair< int, int > >
calculate_ellipse_quarter_coordinates( double inter_center_distance, double radius )
{
    assert( radius > 0 && "Radius must be positive." );
    assert( inter_center_distance < radius && "Radius is too small." );

    std::vector< std::pair< int, int > > coordinates;

    auto leftmost_x = ( radius - ( inter_center_distance ) ) / 2.0;

    coordinates.emplace_back( - leftmost_x, 0 );

    for ( int i = leftmost_x - 1; i >= 0; --i )
    {
        auto d1 = ( pow( i + inter_center_distance, 2 ) - pow( i, 2 ) - pow( radius, 2 ) ) / ( -2 * radius );
        coordinates.emplace_back( -i, sqrt( pow( d1, 2 ) - pow( i, 2 ) ) );
    }

    coordinates.emplace_back( 0, ( pow( inter_center_distance, 2 ) - pow( radius, 2 ) ) / ( -2 * radius ) );

    for ( int i = 1; i < inter_center_distance / 2; ++i )
    {
        auto d1 = ( pow( inter_center_distance - i, 2 ) - pow( i, 2 ) - pow( radius, 2 ) ) / ( -2 * radius );
        coordinates.emplace_back( i, sqrt( pow( d1, 2 ) - pow( i, 2 ) ) );
    }

    return coordinates;
}

void draw_ellipse( const sdl::Renderer& renderer, int x1, int x2, int y, int radius )
{
    if ( x2 < x1 )
    {
        std::swap( x1, x2 );
    }

    assert( radius > 0 && "Radius must be positive." );
    auto inter_center_distance = x2 - x1;
    assert( inter_center_distance < radius && "Radius is too small." );

    auto leftmost_x = ( radius - ( inter_center_distance ) ) / 2.0;

    int prev_x = x1 - leftmost_x;
    int prev_y = y;

    for ( int i = leftmost_x - 1; i >= 0; --i )
    {
        auto d1 = ( pow( i + inter_center_distance, 2 ) - pow( i, 2 ) - pow( radius, 2 ) ) / ( -2 * radius );
        auto curr_y = y - sqrt( pow( d1, 2 ) - pow( i, 2 ) );
        auto curr_x = x1 - i;

        renderer.draw_line( prev_x, prev_y, curr_x, curr_y );

        prev_x = curr_x;
        prev_y = curr_y;
    }

    auto curr_y = y - ( pow( inter_center_distance, 2 ) - pow( radius, 2 ) ) / ( -2 * radius );
    renderer.draw_line( prev_x, prev_y, x1, curr_y );

    prev_x = x1;
    prev_y = curr_y;

    for ( int i = 1; i < inter_center_distance / 2; ++i )
    {
        auto d1 = ( pow( inter_center_distance - i, 2 ) - pow( i, 2 ) - pow( radius, 2 ) ) / ( -2 * radius );
        curr_y = y - sqrt( pow( d1, 2 ) - pow( i, 2 ) );
        auto curr_x = x1 + i;


        renderer.draw_line( prev_x, prev_y, curr_x, curr_y );

        prev_x = curr_x;
        prev_y = curr_y;

    }
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
            draw_ellipse( renderer, 100, 500, 200, 420 );
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
