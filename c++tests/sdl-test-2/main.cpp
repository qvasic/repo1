#include "SDLLibrary.h"
#include "GraphicalElement.h"

#include <SDL2/SDL.h>

#include <iostream>
#include <chrono>
#include <thread>
#include <vector>

#include <cassert>
#include <cmath>

std::vector< std::pair< int, int > >
calculate_ellipse_quarter_coordinates( double inter_center_distance, double radius )
{
    assert( radius > 0 && "Radius must be larger than zero." );
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

template < typename F1, typename F2 >
void
draw_ellipse( const F1& draw_point, const F2& draw_line, int x1, int x2, int y, int radius )
{
    if ( x2 < x1 )
    {
        std::swap( x1, x2 );
    }

    auto coordinates = calculate_ellipse_quarter_coordinates( x2 - x1, radius );

    if ( coordinates.size( ) > 1 )
    {
        for ( size_t i = 1; i < coordinates.size( ); ++i )
        {
            if ( abs( coordinates[ i - 1 ].second - coordinates[ i ].second ) > 1 )
            {
                draw_line( x1 + coordinates[i - 1].first, y + coordinates[i - 1].second,
                           x1 + coordinates[i].first, y + coordinates[i].second );
                draw_line( x1 + coordinates[i - 1].first, y - coordinates[i - 1].second,
                           x1 + coordinates[i].first, y - coordinates[i].second );

                draw_line( x2 - coordinates[i - 1].first, y + coordinates[i - 1].second,
                           x2 - coordinates[i].first, y + coordinates[i].second );
                draw_line( x2 - coordinates[i - 1].first, y - coordinates[i - 1].second,
                           x2 - coordinates[i].first, y - coordinates[i].second );
            }
            else
            {
                draw_point( x1 + coordinates[i].first, y + coordinates[i].second );
                draw_point( x1 + coordinates[i].first, y - coordinates[i].second );
                draw_point( x2 - coordinates[i].first, y + coordinates[i].second );
                draw_point( x2 - coordinates[i].first, y - coordinates[i].second );
            }
        }
    }

    if ( !coordinates.empty( ) )
    {
        draw_line( x1 + coordinates.back( ).first, y + coordinates.back( ).second,
                   x2 - coordinates.back( ).first, y + coordinates.back( ).second );
        draw_line( x1 + coordinates.back( ).first, y - coordinates.back( ).second,
                   x2 - coordinates.back( ).first, y - coordinates.back( ).second );
    }
}

void
draw_ellipse( const sdl::Renderer& renderer, int x1, int y1, int x2, int y2 )
{
    if ( x1 > x2 )
    {
        std::swap( x1, x2 );
    }

    if ( y1 > y2 )
    {
        std::swap( y1, y2 );
    }

    bool inverted_coordinates = false;

    if ( y2 - y1 > x2 - y1 )
    {
        std::swap( x1, y1 );
        std::swap( x2, y2 );
        inverted_coordinates = true;
    }

    auto radius = x2 - x1;
    auto y_max = ( y2 - y1 ) / 2;
    auto x_half = sqrt( pow( radius / 2, 2 ) - pow( y_max, 2 ) );
    auto x_middle = ( x1 + x2 ) / 2;
    auto y_middle = ( y1 + y2 ) / 2;

    if ( inverted_coordinates )
    {
        draw_ellipse( [ &renderer ]( auto x, auto y ){ renderer.draw_point( y, x ); },
                      [ &renderer ]( auto x1, auto y1, auto x2, auto y2 ){ renderer.draw_line( y1, x1, y2, x2 ); },
                      x_middle - x_half, x_middle + x_half, y_middle, radius );
    }
    else
    {
        draw_ellipse( [ &renderer ]( auto x, auto y ){ renderer.draw_point( x, y ); },
                      [ &renderer ]( auto x1, auto y1, auto x2, auto y2 ){ renderer.draw_line( x1, y1, x2, y2 ); },
                      x_middle - x_half, x_middle + x_half, y_middle, radius );
    }
}

int main( int, char** )
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
            if ( x > 1 && y > 1 )
            {
                draw_ellipse( renderer, 0, 0, x, y );
            }
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
