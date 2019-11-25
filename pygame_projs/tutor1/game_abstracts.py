"""Game abstract types
"""

class TextPrinter:
    def __init__( self, surf, color ):
        import pygame
        self.reset()
        self.font = pygame.font.Font( None, 20 )
        self.surf = surf
        self.color = color

    def print_line( self, textString ):
        text_bitmap = self.font.render( textString, True, self.color )
        self.surf.blit( text_bitmap, [self.x, self.y] )
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

class GameLoop:
    """contains main list of GameObjs, reqests them to draw, move,
if it is no longer exists, it is removed from the main list"""

    def __init__( self, screen_size, background, framerate, show_stats=False ):
        import pygame
        import time

        pygame.init()

        self.obj_list = []
        self.framerate = framerate
        self.surf = pygame.display.set_mode( screen_size )
        self.background = background
        self.show_stats = show_stats
        self.printer = TextPrinter( self.surf, (255, 255, 255) )
        self.last_iter = time.time()

    def main_loop( self ):
        import pygame
        import time

        time_for_frame = 1/self.framerate
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            frame_start = time.time()
            move_time = frame_start-self.last_iter
            self.last_iter = frame_start

            self.surf.fill( self.background )

            i = len( self.obj_list )
            while i > 0:
                if not self.obj_list[ i - 1 ].move_and_draw( move_time, self.surf ):
                    self.obj_list.pop(i - 1)
                i -= 1

            if self.show_stats:
                self.printer.reset()
                self.printer.print_line( "stats" )
                self.printer.print_line( "game objs num: {}".format( len( self.obj_list ) ) )
                draw_time = time.time() - frame_start
                time_stats = "frame drawn in: {:.3f}/{:.3f}, {:06.3f}% of time for a frame".format(
                                                          round( draw_time, 2 ),
                                                          round( time_for_frame, 2 ),
                                                          round( draw_time/time_for_frame*100, 1 )
                                                                                 )
                self.printer.print_line( time_stats )

            pygame.display.flip()
            frame_end = time.time()
            sleep_time = time_for_frame - ( frame_end-frame_start )
            if sleep_time > 0:
                time.sleep( sleep_time )

    def add_game_obj( self, new_obj ):
        self.obj_list.append( new_obj )

    def get_obj_list( self ):
        return self.obj_list

class GameObj:
    def move_and_draw( self, time, surf ) -> bool:
        """Move and redraw the object

        Arguments:
        time - amount of time passed since last move;
        surf - pygame surface to draw on.

        Should return True if object still exists
        Should return False if object ceased to exist
        """
        return True

    def check_projectile_impact( self, start, end ):
        """Checks whether projectile impacts the object.

        Arguments:
        start - projectile initial position
        end   - projectile final position
        If object is impacted - returns distance from point start to point of impact.
        If object is not impacted - returns None.
        """
        pass

    def do_projectile_impact( self ):
        """Checks whether projectile impacts the object.

        Arguments:
        from - projectile initial position
        to - projectile final position
        If object is impacted - returns distance from point from to point of impact.
        If object is not impacted - returns None.
        """
        pass

class PlayerInput:
    def get_left_stick_direction( self ) -> tuple:
        pass

    def get_right_stick_direction( self ) -> tuple:
        pass

    def get_right_trigger( self ) -> int:
        pass

    def get_button_a( self ) -> bool:
        pass

    def get_button_b( self ) -> bool:
        pass

if __name__ == "__main__":
    print( __file__, __doc__,
           "this is supposed to be used as a importable module", sep="\n", end="" )
