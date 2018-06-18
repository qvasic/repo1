import game_abstracts
import game_utils

class BouncingBall( game_abstracts.GameObj ):
    def __init__( self, coords, vector, color ):
        self.coords = list( coords )
        self.vector = list( vector )
        self.color = color

    def bounce_off_screen( self, screen_size ):
        if self.coords[0] < 0:
            self.coords[0] = -self.coords[0]
            self.vector[0] = -self.vector[0]

        if self.coords[0] >= screen_size[0]:
            self.coords[0] = screen_size[0]-(self.coords[0]-screen_size[0])
            self.vector[0] = -self.vector[0]

        if self.coords[1] < 0:
            self.coords[1] = -self.coords[1]
            self.vector[1] = -self.vector[1]

        if self.coords[1] >= screen_size[1]:
            self.coords[1] = screen_size[1]-(self.coords[1]-screen_size[1])
            self.vector[1] = -self.vector[1]

    def move_and_draw( self, time, surf ) -> bool:
        import pygame

        self.coords = [ c+m*time for c, m in zip( self.coords, self.vector ) ]
        self.bounce_off_screen( surf.get_size() )
        pygame.draw.circle( surf, self.color, tuple( map( int, self.coords ) ), 2 )

        return True

class BouncingBallWithLives( BouncingBall ):
    def __init__( self, coords, vector, color, lives ):
        BouncingBall.__init__( self, coords, vector, color )
        self.lives = lives

    def bounce_off_screen( self, screen_size ):
        prev_vec = list( self.vector )
        BouncingBall.bounce_off_screen( self, screen_size )
        if prev_vec[0] != self.vector[0]:
            self.lives -= 1
        if prev_vec[1] != self.vector[1]:
            self.lives -= 1

    def move_and_draw( self, time, surf ) -> bool:
        import pygame
        BouncingBall.move_and_draw( self, time, surf )
        pygame.draw.circle( surf, self.color, tuple( map( int, self.coords ) ), self.lives if self.lives>0 else 1 )
        return self.lives > 0

class BallSpawner( game_abstracts.GameObj ):
    def __init__( self, looper, timeout ):
        self.looper = looper
        self.timeout = timeout
        self.elapsed = 0

    def move_and_draw( self, time, surf ) -> bool:
        from random import randrange

        w, h = surf.get_size()

        self.elapsed += time
        if self.elapsed > self.timeout:
            self.looper.add_game_obj( BouncingBallWithLives( (randrange( w ), randrange( h ) ),
                                                      (randrange( 50, 300 ), randrange( 50, 300 )),
                                                      (randrange( 128, 256 ), randrange( 128, 256 ), randrange( 128, 256 )),
                                                      randrange( 5, 15 )
                                                    )
                             )

            self.elapsed -= self.timeout
        return True

class F310GamepadInput( game_abstracts.PlayerInput ):
    def __init__( self ):
        import pygame.joystick

        pygame.joystick.init()
        for i in range( pygame.joystick.get_count() ):
            j = pygame.joystick.Joystick( i )
            if j.get_name().find( "F310" ) != -1:
                j.init()
                self.joy = j
                break
        else:
            raise RuntimeError( "Logitech F310 gamepad not found" )

    def get_direction( self ):
        return self.joy.get_axis( 0 ), self.joy.get_axis( 1 )

    def get_button_a( self ):
        return self.joy.get_button( 0 )

    def get_button_b( self ):
        return self.joy.get_button( 2 )

class AutocanonProjectile( game_abstracts.GameObj ):
    shape = ( ( (0, -2), (0, 2) ), )


    color = ( 255, 255, 255 )
    velocity = 400

    def __init__( self, coords, vector ):
        self.coords = coords
        self.vector = tuple( c*self.velocity for c in vector )

    def move_and_draw( self, time, surf ):
        import pygame
        self.coords = tuple( c+v*time for c, v in zip( self.coords, self.vector ) )

        surfsize = surf.get_size()
        if ( self.coords[0] < 0 or self.coords[0] >= surfsize[0]
          or self.coords[1] < 0 or self.coords[1] >= surfsize[1] ):
            return False

        for l in self.shape:
            l = game_utils.position_polyline( l, self.vector, self.coords )
            pygame.draw.lines( surf, self.color, False, l, 2 )


        return True


class PlayerShipObj( game_abstracts.GameObj ):
    ship_shape = (
        ( (-1, -6), (1, -6) ),
        ( (-1, -20), (-2, -6), (-4, -3), (-7, 0 ), (-2, 10),
            (2, 10), (7, 0), (4, -3), (2, -6), (1, -20), (-1, -20) ),
        ( (-6, 1), (-18, 6), (-17, 14), (-16, 8), (-10, 7), (-4, 8) ),
        ( (4, 8), (10, 7), (16, 8), (17, 14), (18, 6), (6, 1) ),

        ( (-7, 0), (-7, -5), (-6, -5), (-6, -1) ),
        ( (7, 0), (7, -5), (6, -5), (6, -1) ),
    )
    color = (255, 255, 255)
    screen_wall = 30
    fire_rate = 20
    gun_ports = ( (-6, -5), (6, -5) )

    def __init__( self, coords, input, looper ):
        self.input = input
        self.coords = coords
        self.inertia = [ 0, 0 ]
        self.orientation = [ 0, -0.1 ]
        self.full_throttle = 300
        self.time_since_last_shot = 1
        self.cur_gun_port = 0
        self.looper = looper

    def contain_inside_screen( self, size ):
        if self.coords[0] < self.screen_wall and self.inertia[0] < 0:
            self.inertia[0] = 0
        if self.coords[0] > size[0]-self.screen_wall and self.inertia[0] > 0:
            self.inertia[0] = 0
        if self.coords[1] < self.screen_wall and self.inertia[1] < 0:
            self.inertia[1] = 0
        if self.coords[1] > size[1]-self.screen_wall and self.inertia[1] > 0:
            self.inertia[1] = 0

    def get_gun_port( self ):
        ret_gun_port = self.gun_ports[ self.cur_gun_port ]
        self.cur_gun_port += 1
        if self.cur_gun_port == len( self.gun_ports ):
            self.cur_gun_port = 0
        return ret_gun_port

    def move_and_draw( self, time, surf ):
        import pygame

        input_direction = self.input.get_direction()
        if abs(input_direction[0])>0.1 or abs(input_direction[1])>0.1:
            self.orientation = input_direction

        if self.input.get_button_a():
            self.inertia = [ i + ( t * time * self.full_throttle )
                             for i, t in zip( self.inertia, self.orientation ) ]

        self.contain_inside_screen( surf.get_size() )

        self.coords = [ c+time*i for c, i in zip( self.coords, self.inertia ) ]

        for l in self.ship_shape:
            l = game_utils.position_polyline( l, self.orientation, self.coords )
            pygame.draw.lines( surf, self.color, False, l, 1 )

        self.time_since_last_shot += time
        if self.input.get_button_b() and self.time_since_last_shot > 1/self.fire_rate:

            proj_init_pos = game_utils.rotate_vec( self.get_gun_port(),
                                                   self.orientation, self.coords )
            self.looper.add_game_obj( AutocanonProjectile( proj_init_pos,
                                     game_utils.redirect_vec( (0,-1), self.orientation ) ) )
            self.time_since_last_shot = 0

        return True

class StubGameLoop( game_abstracts.GameLoop ):
    def __init__( self ):
        w = 800
        h = 600

        game_abstracts.GameLoop.__init__( self, ( w, h ), (0, 0, 0), 60, True )

        """from random import randrange
        for i in range( randrange( 10 )+10 ):
            self.add_game_obj( BouncingBall( (randrange( w ), randrange( h ) ),
                                             (randrange( 50, 400 ), randrange( 50, 400 )),
                                             (randrange( 128, 256 ), randrange( 128, 256 ), randrange( 128, 256 ))
                                           )
                             )

        self.add_game_obj( BallSpawner( self, 1 ) )
        """

        gamepad = F310GamepadInput()
        player_ship = PlayerShipObj( (200, 200), gamepad, self )
        self.add_game_obj( player_ship )

def main():
    looper = StubGameLoop()
    looper.main_loop()

if __name__ == "__main__":
    main()
