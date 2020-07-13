#ifndef GRAPHICALELEMENT_H_OASDFUIHASOUDFIASODIUFH2P34HRF2349
#define GRAPHICALELEMENT_H_OASDFUIHASOUDFIASODIUFH2P34HRF2349

#include "SDLLibrary.h"

class GraphicalElement
{
public:
    virtual void draw( const sdl::Renderer& ) = 0;
};

class GraphicalGroup : public GraphicalElement
{};

class Line : public GraphicalElement
{};

class Ellipse : public GraphicalElement
{};

class Rectangle : public GraphicalElement
{};

#endif // GRAPHICALELEMENT_H
