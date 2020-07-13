#include "SDLLibrary.h"

#include <stdexcept>
#include <string>

sdl::Library::Library( Uint32 flags )
{
    if ( SDL_Init( flags ) != 0 )
    {
        throw std::runtime_error( std::string( "Could not initialize SDL video system: " ) + SDL_GetError( ) );
    }
}

sdl::Library::~Library()
{
    SDL_Quit( );
}

sdl::Renderer::Renderer( SDL_Renderer* sdl_renderer_ptr )
    : m_sdl_renderer_ptr( sdl_renderer_ptr )
{}

sdl::Renderer::~Renderer( )
{
    SDL_DestroyRenderer( m_sdl_renderer_ptr );
}


void sdl::Renderer::clear( )
{
    SDL_RenderClear( m_sdl_renderer_ptr );
}

void sdl::Renderer::present( )
{
    SDL_RenderPresent( m_sdl_renderer_ptr );
}

void sdl::Renderer::set_draw_color( Uint8 r, Uint8 g, Uint8 b, Uint8 a )
{
    SDL_SetRenderDrawColor( m_sdl_renderer_ptr, r, g, b, a );
}

void sdl::Renderer::draw_line( int x1, int y1, int x2, int y2 ) const
{
    SDL_RenderDrawLine( m_sdl_renderer_ptr, x1, y1, x2, y2 );
}

void sdl::Renderer::draw_point( int x, int y ) const
{
    SDL_RenderDrawPoint( m_sdl_renderer_ptr, x, y );
}

sdl::Window::Window( const char *title, int x, int y, int w, int h, Uint32 flags )
    : m_sdl_window_ptr( SDL_CreateWindow( title, x, y, w, h, flags ) )
{
    if ( m_sdl_window_ptr == nullptr )
    {
        throw std::runtime_error( std::string( "Could not create SDL window: " ) + SDL_GetError( ) );
    }
}

sdl::Renderer sdl::Window::create_accelerated_renderer( )
{
    auto* sdl_renderer_ptr = SDL_CreateRenderer( m_sdl_window_ptr, -1, SDL_RENDERER_ACCELERATED );
    if ( sdl_renderer_ptr == nullptr )
    {
        throw std::runtime_error( std::string( "Could not create SDL renderer: " ) + SDL_GetError( ) );
    }
    return Renderer( sdl_renderer_ptr );
}

sdl::Window::~Window()
{
    SDL_DestroyWindow( m_sdl_window_ptr );
}
