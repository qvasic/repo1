'''pygame tutorial excercise'''

def rotate_polyline( polyline, vec ):
    import pygame.math
    angle = -pygame.math.Vector2( vec ).angle_to( (0, -1) )
    return [ list( pygame.math.Vector2( p ).rotate( angle ) ) for p in polyline ]

class TextPrint:
    def __init__(self, screen, color):
        import pygame
        self.reset()
        self.font = pygame.font.Font(None, 20)
        self.screen = screen
        self.color = color

    def print(self, textString):
        textBitmap = self.font.render(textString, True, self.color )
        self.screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

class ProjectilesList(list):
    def __init__( self, speed, screen_size ):
        self.move_scale = 10
        self.screen_size = screen_size

    def move( self ):
        i=0
        while i < len( self ):
            p = self[i]
            p[0] = [ c+r*self.move_scale for c, r in zip( p[0], p[1] ) ]
            if ( p[0][0] < 0 or p[0][0] >= self.screen_size[0] or
                 p[0][1] < 0 or p[0][1] >= self.screen_size[1] ):
                self.pop( i )
            else:
                i+=1


class DirectionInput:
    def __init__( self ):
        import pygame
        self.joy = pygame.joystick.Joystick( 1 )
        self.joy.init()

    def get_vector( self ):
        return self.joy.get_axis(0), self.joy.get_axis(1)

def main():
    import pygame
    from random import randrange
    import time
    import vector

    pygame.init()

    size = width, height = 800, 600
    background = 0, 0, 0
    foreground = 255, 255, 255
    scale = 7
    start = 130, 47
    framerate = 60

    curpos = [ c//2 for c in size ]
    last_nonzero_vector = [ 0, -1 ]
    move_scale = 5
    ship_polyline = ( (-2, 2), (0, -5), (2, 2 ) )

    projs = ProjectilesList( 10, size )

    screen = pygame.display.set_mode( size )

    dirinput = DirectionInput()

    printer = TextPrint( screen, (255, 255, 255) )

    exit = False
    while not exit:
        curvec = [ round( c, 1 ) for c in dirinput.get_vector() ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
            if event.type == pygame.JOYBUTTONDOWN:
                projs.append( [ curpos, vector.redirect( (1,0), last_nonzero_vector ) ] )

        if not exit:
            # move stuff
            curpos = [ c+r*move_scale for c, r in zip( curpos, curvec ) ]
            if curvec[0] or curvec[1]:
                last_nonzero_vector = curvec
            projs.move()

            # draw stuff
            screen.fill( background )

            printer.reset()
            printer.print( "stats" )
            printer.print( "curpos: {}".format( [ round( c, 2 ) for c in curpos ] ) )
            printer.print( "curvec: {}".format( [ round( c, 2 ) for c in curvec ] ) )
            printer.print( "lastvec: {}".format( [ round( c, 2 ) for c in last_nonzero_vector ] ) )
            printer.print( "number of projectiles: {}".format( len( projs ) ) )

            pygame.draw.line( screen, foreground,
                                      start,
                                      tuple( s+r*scale for s, r in zip( start, curvec ) ),
                                      2 )
            cur_ship_polyline = [ (p[0]+curpos[0], p[1]+curpos[1])
                                  for p in rotate_polyline( ship_polyline, last_nonzero_vector ) ]
            pygame.draw.lines( screen, foreground, False, cur_ship_polyline, 2 )


            for p in projs:
                pygame.draw.circle( screen, foreground, tuple( map( int, p[0] ) ), 2 )
            pygame.display.flip()
            time.sleep( 1/framerate )


if __name__ == '__main__':
    main()
