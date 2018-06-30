class TextPrinter:
    def __init__( self, surf, color ):
        import pygame
        self.reset()
        self.font = pygame.font.SysFont( "Courier", 18, bold=True )
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

def change_value( val, step, min, max ):
    assert min<max
    if val+step > max:
        return max
    elif val+step < min:
        return min
    else:
        return val+step

def speed_ms_to_kmh( ms ):
    return ms*3600/1000

class Driver:
    def __init__( self, coords_setter_callback=None ):
        self.update_coords = coords_setter_callback

    def run( self ):
        import pygame, time, vehicle_phys

        refresh_rate = 10
        ctrl_step_big = 0.05
        ctrl_step_sml = 0.01

        pygame.init()

        surface = pygame.display.set_mode( ( 600, 100 ) )
        printer = TextPrinter( surface, (0, 192, 0) )
        vehicle = vehicle_phys.VehicleOnEarthSurface( )

        vehicle.lat = 49.802975
        vehicle.lng = 24.000613

        steering = 0
        throttle = 0
        brake = 0

        last_move_time = time.time( )

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    ctrl_step = ctrl_step_sml if event.mod & pygame.KMOD_CTRL else ctrl_step_big

                    if event.mod & pygame.KMOD_SHIFT:
                        if event.key == pygame.K_DOWN:
                            brake = change_value( brake, -ctrl_step, 0, 1 )
                        elif event.key == pygame.K_UP:
                            brake = change_value( brake, ctrl_step, 0, 1 )

                    elif event.mod == pygame.KMOD_NONE or event.mod & pygame.KMOD_CTRL:
                        if event.key == pygame.K_LEFT:
                            steering = change_value( steering, -ctrl_step, -1, 1 )
                        elif event.key == pygame.K_RIGHT:
                            steering = change_value( steering, ctrl_step, -1, 1 )
                        elif event.key == pygame.K_DOWN:
                            throttle = change_value( throttle, -ctrl_step, 0, 1 )
                        elif event.key == pygame.K_UP:
                            throttle = change_value( throttle, ctrl_step, 0, 1 )


            now = time.time( )
            vehicle.move( now-last_move_time, steering, throttle, brake )
            last_move_time = now

            surface.fill( (0, 0, 0) )
            printer.reset( )
            printer.print_line( "steering: {:5.2f} throttle: {:.2f} brake: {:.2f}".format(
                steering, throttle, brake ) )
            printer.print_line( "lat: {:.3f} lng: {:.3f} bearing: {:.0f} speed: {:6.1f}".format(
                vehicle.lat, vehicle.lng, vehicle.bearing_deg, speed_ms_to_kmh( vehicle.speed_m_s ) ) )

            pygame.display.flip( )

            if self.update_coords:
                self.update_coords( vehicle.lat, vehicle.lng, vehicle.speed_m_s, vehicle.bearing_deg )

            time.sleep( 1/refresh_rate )

def main( ):
    d = Driver( )
    d.run( )

if __name__ == "__main__":
    main( )
