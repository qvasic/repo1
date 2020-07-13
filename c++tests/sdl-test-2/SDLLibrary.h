#ifndef SDLLIBRARY_H_A0S98FDHJA0S98DFHJAS0F98HE0F8F
#define SDLLIBRARY_H_A0S98FDHJA0S98DFHJAS0F98HE0F8F

#include <SDL2/SDL.h>

namespace sdl
{

class Library
{
public:
    Library( Uint32 flags );
    ~Library();
};

class Renderer
{
public:
    explicit Renderer( SDL_Renderer* sdl_renderer_ptr );
    ~Renderer( );
    void clear( );
    void present( );
    void set_draw_color( Uint8 r, Uint8 g, Uint8 b, Uint8 a );
    void draw_line( int x1, int y1, int x2, int y2 ) const;
    void draw_point( int x, int y ) const;

private:
    SDL_Renderer* m_sdl_renderer_ptr;
};

class Window
{
public:
    Window( const char *title, int x, int y, int w, int h, Uint32 flags );
    Renderer create_accelerated_renderer( );
    ~Window();

private:
    SDL_Window* m_sdl_window_ptr;
};

} // namespace sdl

#endif // SDLLIBRARY_H
