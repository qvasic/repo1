class TextPrinter:
    font = None
    def draw_text( surf, coords, text, color, centered=False ):
        import pygame
        if TextPrinter.font is None:
            TextPrinter.font = pygame.font.SysFont( "Courier", 18, bold=True )

        text_bitmap = TextPrinter.font.render( text, True, color )
        if centered:
            printed_size = text_bitmap.get_size( )
            coords = coords[0]-printed_size[0]/2, coords[1]-printed_size[1]/2
        surf.blit( text_bitmap, coords )

    def __init__( self, surf, color, start ):
        self.start = start
        self.reset()
        self.surf = surf
        self.color = color

    def print_line( self, text ):
        TextPrinter.draw_text( self.surf, ( self.x, self.y ), text, self.color )
        self.y += self.line_height

    def reset(self):
        self.x, self.y = self.start
        self.line_height = 15

def sum_coords( *coords ):
    """Returns sum of all coords passed here - expects subscribeable objects with indeces 0 and 1."""
    sum = [ 0, 0 ]
    for c in coords:
        sum[0]+=c[0]
        sum[1]+=c[1]
    return sum

def draw_wheels( surface, color, turn_deg ):
    import pygame
    from earth_walk import coords
    wheel_r = 7
    center = ( 75, 80 )
    vwid, vlen = 30, 50
    thick = 6

    x, y = coords( 90+turn_deg, wheel_r )
    pygame.draw.line( surface, color, sum_coords( (x,y), center, (-vwid/2, -vlen/2) ),
                                      sum_coords( (-x,-y), center, (-vwid/2, -vlen/2) ), thick )
    pygame.draw.line( surface, color, sum_coords( (x,y), center, (vwid/2, -vlen/2) ),
                                      sum_coords( (-x,-y), center, (vwid/2, -vlen/2) ), thick )

    pygame.draw.line( surface, color, sum_coords( (0,wheel_r), center, (-vwid/2, vlen/2) ),
                                      sum_coords( (0,-wheel_r), center, (-vwid/2, vlen/2) ), thick )
    pygame.draw.line( surface, color, sum_coords( (0,wheel_r), center, (vwid/2, vlen/2) ),
                                      sum_coords( (0,-wheel_r), center, (vwid/2, vlen/2) ), thick )

def draw_compass( surface, color, bearing_deg ):
    import pygame
    from earth_walk import coords
    center = ( 75, 80 )

    letters = ( ( 0, "N", 55 ),
    )
    marks = ( ( ( 90, 180, 270 ), 55, 10, 3),
              ( ( 45, 135, 225, 315 ), 55, 7, 1 ),
    )

    for d, l, r in letters:
        c = sum_coords( coords( d-bearing_deg-90, r ), center )
        TextPrinter.draw_text( surface, c, l, color, centered=True )

    for ms, r, l, th in marks:
        for m in ms:
            fr = sum_coords( coords( m-bearing_deg-90, r-l/2 ), center )
            to = sum_coords( coords( m-bearing_deg-90, r+l/2 ), center )
            pygame.draw.line( surface, color, fr, to, th )

class VehicleDriver:
    def __init__( self, coords_setter_callback=None ):
        self.update_coords = coords_setter_callback

    def run( self, start_coords=None ):
        import pygame, time, vehicle_phys, input_devices

        def speed_ms_to_kmh( ms ):
            return ms*3600/1000

        refresh_rate = 30
        ctrl_step_big = 0.05
        ctrl_step_sml = 0.01

        pygame.init( )

        text_color = (0, 192, 0)
        wheels_color = (64, 92, 64)
        compass_color = (128, 128, 0)

        surface = pygame.display.set_mode( ( 400, 165 ) )
        printer = TextPrinter( surface, text_color, ( 150, 10 ) )
        vehicle = vehicle_phys.VehicleOnEarthSurface( )

        user_input = input_devices.get_available_input( )

        if start_coords is None:
            # san francisco
            # vehicle.lat, vehicle.lng = 37.807973, -122.442499

            # lviv, naukova
            vehicle.lat, vehicle.lng = 49.803076, 24.000658

            # berlin, here hq
            # vehicle.lat, vehicle.lng = 52.531016, 13.384984
        else:
            vehicle.lat, vehicle.lng = start_coords

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

            draw_wheels( surface, wheels_color, user_input.get_steering( ) * vehicle.max_front_turn_deg )
            draw_compass( surface, compass_color, vehicle.bearing_deg )

            printer.reset( )
            printer.print_line( "throttle:  {:.2f}".format( user_input.get_throttle( ) ) )
            printer.print_line( "brake:     {:.2f}".format( user_input.get_brake( ) ) )
            printer.print_line( "steering: {:5.2f}".format( user_input.get_steering( ) ) )
            printer.print_line( "" )
            printer.print_line( "speed:  {:6.1f} km/h".format( speed_ms_to_kmh( vehicle.speed_m_s ) ) )
            printer.print_line( "" )
            printer.print_line( "lat:     {:9.5f}".format( vehicle.lat ) )
            printer.print_line( "lng:    {:10.5f}".format( vehicle.lng ) )
            printer.print_line( "bearing: {:3.0f}".format( vehicle.bearing_deg ) )

            pygame.display.flip( )

            if self.update_coords:
                self.update_coords( vehicle.lat, vehicle.lng, vehicle.speed_m_s, vehicle.bearing_deg )

            time.sleep( 1/refresh_rate )

class DumpCoordsWithFreq:
    """Creates callable object. Can be called with positional info,
    that info will dumped to stdout no more than given number of times per second."""

    def __init__( self, freq ):
        import time

        self.interval = 1/freq
        self.next_dump_timestamp = time.time( )

    def __call__( self, lat, lng, speed_m_s, bearing ):
        import time

        timestamp = time.time( )
        if timestamp >= self.next_dump_timestamp:
            print( lat, lng, 0, bearing, speed_m_s, flush=True )
            self.next_dump_timestamp += self.interval


def main( ):
    d = VehicleDriver( DumpCoordsWithFreq( 1 ) )
    d.run( )

if __name__ == "__main__":
    main( )
