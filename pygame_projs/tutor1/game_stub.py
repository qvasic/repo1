import game_abstracts
import game_utils

class BouncingBall( game_abstracts.GameObj ):
    def __init__( self, coords, vector, color, size = 2 ):
        self.coords = list( coords )
        self.vector = list( vector )
        self.color = color
        self.size = size

    def bounce_off_screen( self, screen_size ):
        margin = self.size / 2
        if self.coords[0] < margin:
            self.vector[0] = -self.vector[0]

        if self.coords[0] >= screen_size[0] - margin:
            self.vector[0] = -self.vector[0]

        if self.coords[1] < margin:
            self.vector[1] = -self.vector[1]

        if self.coords[1] >= screen_size[1] - margin:
            self.vector[1] = -self.vector[1]

    def move_and_draw( self, time, surf ) -> bool:
        import pygame

        self.coords = [ c+m*time for c, m in zip( self.coords, self.vector ) ]
        self.bounce_off_screen( surf.get_size() )
        pygame.draw.circle( surf, self.color, tuple( map( int, self.coords ) ), int( self.size ) )

        return True

class ImpactableBouncingBall( BouncingBall ):
    def __init__( self, coords, vector, color, size = 2 ):
        BouncingBall.__init__( self, coords, vector, color, size )

    def check_projectile_impact( self, start, end ):
        if self.size <= 0:
            return

        start = game_utils.Point( start[ 0 ], start[ 1 ] )
        end = game_utils.Point( end[ 0 ], end[ 1 ] )
        center = game_utils.Point( self.coords[ 0 ], self.coords[ 1 ] )

        intersections = game_utils.intersect_line_segment_and_circle( game_utils.Circle( center, self.size ),
                                                                      game_utils.LineSegment( start, end ) )

        if len( intersections ) > 1 or ( len(intersections) == 1 and game_utils.distance( center, start ) > self.size ):
            impact_point = intersections[0]
            impact_surface = game_utils.Line( impact_point, center ).perpendicular( impact_point )
            return ( impact_point, impact_surface )

class ImpactableBouncingBallWithLives( ImpactableBouncingBall ):
    def __init__( self, coords, vector, color, lives ):
        ImpactableBouncingBall.__init__( self, coords, vector, color, lives )

    def move_and_draw( self, time, surf ) -> bool:
        #import pygame
        BouncingBall.move_and_draw( self, time, surf )
        return self.size > 3

    def do_projectile_impact(self):
        self.size -= 0.4

class BallSpawner( game_abstracts.GameObj ):
    def __init__( self, looper, timeout ):
        self.looper = looper
        self.timeout = timeout
        self.elapsed = timeout

    def move_and_draw( self, time, surf ) -> bool:
        from random import randrange

        w, h = surf.get_size()

        self.elapsed += time
        if self.elapsed >= self.timeout:
            self.looper.add_game_obj( ImpactableBouncingBallWithLives( (randrange( w ), randrange( h ) ),
                                                                       (randrange( 25, 50 ), randrange( 25, 50 )),
                                                                       (randrange( 128, 256 ), randrange( 128, 256 ),
                                                                        randrange( 128, 256 )),
                                                                       randrange( 15, 25 )
                                                                     )
                             )

            self.elapsed -= self.timeout
        return True

class GamepadInput( game_abstracts.PlayerInput ):
    def __init__( self ):
        import pygame.joystick

        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No game controller present.")

        self.joy = pygame.joystick.Joystick( 0 )
        self.joy.init( )

        self.stick_axis_threshold = 0.15

        return

    def get_left_stick_direction( self ):
        return game_utils.apply_threshold( ( self.joy.get_axis( 0 ), self.joy.get_axis( 1 ) ),
                                           self.stick_axis_threshold )

    def get_right_stick_direction( self ):
        return game_utils.apply_threshold( ( self.joy.get_axis( 4 ), self.joy.get_axis( 3 ) ),
                                           self.stick_axis_threshold )

    def get_right_trigger( self ):
        axis = self.joy.get_axis( 2 )
        if axis > 0:
            return 0

        return abs( axis )

    def get_button_a( self ):
        return self.joy.get_button( 0 )

    def get_button_b( self ):
        return self.joy.get_button( 2 )

class AutocanonProjectile( game_abstracts.GameObj ):
    shape = ( ( (0, -5), (0, 5) ), )
    color = ( 255, 255, 64 )
    velocity = 400

    def __init__( self, game_loop, coords, vector ):
        self.game_loop = game_loop
        self.coords = coords
        self.vector = tuple( c*self.velocity for c in vector )

    def move_and_draw( self, time, surf ):
        import pygame
        next_coords = tuple( c+v*time for c, v in zip( self.coords, self.vector ) )

        nearest_impact_obj = None
        nearest_impact_data = None
        nearest_impact_dist = None
        for obj in self.game_loop.get_obj_list( ):
            impact_data = obj.check_projectile_impact( self.coords, next_coords )
            if impact_data:
                impact_dist = game_utils.distance( impact_data[ 0 ],
                                                   game_utils.Point( self.coords[ 0 ], self.coords[ 1 ] ) )
                if not nearest_impact_obj or nearest_impact_dist > impact_dist:
                    nearest_impact_obj = obj
                    nearest_impact_dist = impact_dist
                    nearest_impact_data = impact_data

        if nearest_impact_obj:
            nearest_impact_obj.do_projectile_impact( )
            ricochet_position = nearest_impact_data[ 1 ].mirror( game_utils.Point( next_coords[ 0 ], next_coords[ 1 ] ) )
            next_coords = [ ricochet_position.x, ricochet_position.y ]
            nearest_impact_data[ 1 ].b = 0
            ricochet_vector = nearest_impact_data[ 1 ].mirror( game_utils.Point( self.vector[ 0 ], self.vector[ 1 ] ) )
            self.vector = [ ricochet_vector.x, ricochet_vector.y ]

        self.coords = next_coords

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
    color = (96, 192, 96)
    screen_wall = 30
    fire_rate = 20
    gun_ports = ( (-6, -5), (6, -5) )

    def __init__( self, coords, input, game_loop ):
        self.input = input
        self.coords = coords
        self.inertia = [ 0, 0 ]
        self.orientation = [ 0, -0.1 ]
        self.full_throttle = 300
        self.time_since_last_shot = 1
        self.cur_gun_port = 0
        self.game_loop = game_loop

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

        input_direction = self.input.get_right_stick_direction()
        if abs(input_direction[0])>0.1 or abs(input_direction[1])>0.1:
            self.orientation = input_direction

        self.inertia = [ (t * self.full_throttle)
                                        for i, t in zip(self.inertia, self.input.get_left_stick_direction())]

        self.contain_inside_screen( surf.get_size() )

        self.coords = [ c+time*i for c, i in zip( self.coords, self.inertia ) ]

        for l in self.ship_shape:
            l = game_utils.position_polyline( l, self.orientation, self.coords )
            pygame.draw.lines( surf, self.color, False, l, 1 )

        self.time_since_last_shot += time
        if self.input.get_right_trigger() > 0.5 and self.time_since_last_shot > 1/self.fire_rate:

            proj_init_pos = game_utils.rotate_vec( self.get_gun_port(),
                                                   self.orientation, self.coords )
            self.game_loop.add_game_obj( AutocanonProjectile( self.game_loop, proj_init_pos,
                                         game_utils.redirect_vec( (0,-2), self.orientation ) ) )
            self.time_since_last_shot = 0

        return True


class StubGameLoop( game_abstracts.GameLoop ):
    def __init__( self ):
        w = 800
        h = 600

        game_abstracts.GameLoop.__init__( self, ( w, h ), (0, 0, 0), 60, True )

        gamepad = GamepadInput()
        self.obj = PlayerShipObj((200, 200), gamepad, self)
        player_ship = self.obj
        self.add_game_obj( player_ship )

        from random import randrange
        for i in range( randrange( 5 )+5 ):
            self.add_game_obj( BouncingBall( (randrange( w ), randrange( h ) ),
                                             (randrange( 50, 400 ), randrange( 50, 400 )),
                                             (randrange( 96, 128 ), randrange( 96, 128 ), randrange( 96, 128 ))
                                           )
                             )

        for i in range( 2 ):
            self.add_game_obj( ImpactableBouncingBall( (randrange( w ), randrange( h ) ),
                                                       (randrange( 25, 40 ), randrange( 25, 40 )),
                                                       (randrange( 96, 128 ), randrange( 96, 128 ), randrange( 96, 128 )),
                                                       35
                                           )
                             )


        self.add_game_obj( BallSpawner( self, 5 ) )


def main():
    looper = StubGameLoop()
    looper.main_loop()


if __name__ == "__main__":
    main()
