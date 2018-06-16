import game_abstracts

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

class StubGameLoop( game_abstracts.GameLoop ):
    def __init__( self ):
        w = 800
        h = 600

        game_abstracts.GameLoop.__init__( self, ( w, h ), (0, 0, 0), 60, True )

        from random import randrange
        for i in range( randrange( 50 )+50 ):
            self.add_game_obj( BouncingBall( (randrange( w ), randrange( h ) ),
                                             (randrange( 50, 400 ), randrange( 50, 400 )),
                                             (randrange( 128, 256 ), randrange( 128, 256 ), randrange( 128, 256 ))
                                           )
                             )

        self.add_game_obj( BallSpawner( self, 1 ) )

def main():
    looper = StubGameLoop()
    looper.main_loop()

if __name__ == "__main__":
    main()
