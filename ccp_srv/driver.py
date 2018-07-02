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

class UserInput:
    """Abstract class for getting steering, throttle and brake control input from human user.
    User of this class and its subclasses will get steering, throttle and brake values by
    calling corresponding getters.
    Also for each event process_pygame_event will be called,
    if True is returned - this event was consumed,
    if False is returned - it wasn't consumed and this event should be processed further."""
    def get_steering( self ):
        pass
    def get_throttle( self ):
        pass
    def get_brake( self ):
        pass
    def process_pygame_event( self, event ):
        pass

class KeyboardInput( UserInput ):
    """Input from keyboard."""
    def __init__( self ):
        self.steering = 0
        self.throttle = 0
        self.brake = 0

        self.step_big = 0.1
        self.step_small = 0.01

    def get_steering( self ):
        return self.steering

    def get_throttle( self ):
        return self.throttle

    def get_brake( self ):
        return self.brake

    def change_value( val, step, min, max ):
        assert min<max
        if val+step > max:
            return max
        elif val+step < min:
            return min
        else:
            return val+step

    def process_pygame_event( self, event ):
        import pygame

        change_value = KeyboardInput.change_value

        if event.type == pygame.KEYDOWN:
            ctrl_step = self.step_small if event.mod & pygame.KMOD_CTRL else self.step_big

            if event.mod & pygame.KMOD_SHIFT:
                if event.key == pygame.K_DOWN:
                    self.brake = change_value( self.brake, -ctrl_step, 0, 1 )
                    return True
                elif event.key == pygame.K_UP:
                    self.brake = change_value( self.brake, ctrl_step, 0, 1 )
                    return True

            elif event.mod == pygame.KMOD_NONE or event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_LEFT:
                    self.steering = change_value( self.steering, -ctrl_step, -1, 1 )
                    return True
                elif event.key == pygame.K_RIGHT:
                    self.steering = change_value( self.steering, ctrl_step, -1, 1 )
                    return True
                elif event.key == pygame.K_DOWN:
                    self.throttle = change_value( self.throttle, -ctrl_step, 0, 1 )
                    return True
                elif event.key == pygame.K_UP:
                    self.throttle = change_value( self.throttle, ctrl_step, 0, 1 )
                    return True

        return False

class LogitechF310Input( UserInput ):
    def __init__( self ):
        import pygame
        for i in range( pygame.joystick.get_count( ) ):
            self.joy = pygame.joystick.Joystick( i )
            if self.joy.get_name( ) == "Controller (Gamepad F310)":
                self.joy.init( )
                return
        else:
            raise RuntimeError( "Logitech F310 gamepad could not be found" )

    def get_steering( self ):
        return round( self.joy.get_axis( 0 ), 2 )

    def get_throttle( self ):
        axis3 = round( self.joy.get_axis( 2 ), 2 )
        if axis3 < 0:
            return -axis3
        else:
            return 0

    def get_brake( self ):
        axis3 = round( self.joy.get_axis( 2 ), 2 )
        if axis3 > 0:
            return axis3
        else:
            return 0

    def process_pygame_event( self, event ):
        return False

class Driver:
    def __init__( self, coords_setter_callback=None ):
        self.update_coords = coords_setter_callback

    def run( self ):
        import pygame, time, vehicle_phys

        def speed_ms_to_kmh( ms ):
            return ms*3600/1000

        refresh_rate = 30
        ctrl_step_big = 0.05
        ctrl_step_sml = 0.01

        pygame.init( )

        surface = pygame.display.set_mode( ( 700, 70 ) )
        printer = TextPrinter( surface, (0, 192, 0) )
        vehicle = vehicle_phys.VehicleOnEarthSurface( )

        try:
            user_input = LogitechF310Input( )
        except RuntimeError:
            user_input = KeyboardInput( )

        vehicle.lat = 37.807973
        vehicle.lng = -122.442499

        last_move_time = time.time( )

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                user_input.process_pygame_event( event )


            now = time.time( )
            vehicle.move( now-last_move_time, user_input.get_steering( ),
                                              user_input.get_throttle( ),
                                              user_input.get_brake( ) )
            last_move_time = now

            surface.fill( (0, 0, 0) )
            printer.reset( )
            printer.print_line( "steering: {:5.2f} throttle: {:.2f} brake: {:.2f}".format(
                                                                        user_input.get_steering( ),
                                                                        user_input.get_throttle( ),
                                                                        user_input.get_brake( ) ) )
            printer.print_line( "lat: {:7.3f} lng: {:8.3f} bearing: {:3.0f} speed: {:6.1f} km/h".format(
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
