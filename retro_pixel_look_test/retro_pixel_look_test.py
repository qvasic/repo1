import time
import pygame

class RetroPixelLookWindow:
    def __init__(self):
        self.WINDOW_SIZE = ( 900, 600 )
        self.PIXEL_SIZE = 3
        self.BACKGROUND_COLOR = ( 255, 255, 255 )
        self.UPDATE_RATE = 90

    def draw_data(self, surface):
        surface.fill( self.BACKGROUND_COLOR )

        pygame.draw.line( surface, ( 0, 0, 0 ), ( 10, 10 ), ( 10, 300 ) )
        pygame.draw.line( surface, ( 0, 0, 0 ), ( 10, 300 ), ( 300, 300 ) )
        pygame.draw.circle( surface, ( 0, 0, 0 ), ( 150, 150 ), 150 )

        origin_size = surface.get_size( )
        rescale_size = ( origin_size[0] // self.PIXEL_SIZE, origin_size[1] // self.PIXEL_SIZE )
        rescale_surface = pygame.transform.scale( surface, rescale_size )
        pygame.transform.scale( rescale_surface, origin_size, surface )

    def run(self):
        pygame.init()
        pygame.display.set_caption("retro pixel look test")
        screen = pygame.display.set_mode( self.WINDOW_SIZE )

        self.draw_data( screen )
        pygame.display.flip()

        done = False

        self.redraw = False

        while not done:
            self.redraw = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            if done:
                break

            if not self.redraw:
                time.sleep( 1/self.UPDATE_RATE )
                continue

            self.draw_data( screen )
            pygame.display.flip()

        pygame.quit()

def main( ):
    window = RetroPixelLookWindow( )
    window.run( )

if __name__ == "__main__":
    main( )

