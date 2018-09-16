class InputDeviceUnavailable( RuntimeError ):
    def __init__( self, what ):
        RuntimeError.__init__( self, what )

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
        import pygame.key
        pygame.key.set_repeat( 200, 100 )

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
            ctrl_step = self.step_big if event.mod & pygame.KMOD_SHIFT else self.step_small

            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_DOWN:
                    self.brake = change_value( self.brake, -ctrl_step, 0, 1 )
                    return True
                elif event.key == pygame.K_UP:
                    self.brake = change_value( self.brake, ctrl_step, 0, 1 )
                    return True
            else:
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

def get_angle( x, y ):
    """Returns angle between negative Y axis (going up) and vector (0,0)-(x,y).
    Right halfplane (positive X) contain positive angles, left one (negative X) - negative.
    Calling get_angle( 0,0 ) results in exception ValueError raised."""

    if x == 0:
        if y == 0:
            raise ValueError( "get_angle( 0, 0 ) - "
                              "angle between a line and a point is not defined" )
        elif y < 0:
            return 0
        else:
            return 180

    import math
    if x > 0:
        return math.atan( y / x ) * ( 180 / math.pi ) + 90
    else:
        return -( math.atan( y / -x ) * ( 180 / math.pi ) + 90 )

class StickAngle:
    """State class that keeps track of how many times gamepad stick was rotated."""

    def __init__( self, max_angle, treshold_min, treshold_max ):
        self.max_angle = max_angle
        self.treshold_min = treshold_min
        self.treshold_max = treshold_max

        self.prev_angle = None
        self.base_angle = 0
        self.rotations_offset_angle = 0

    def update_angle( self, x, y ):
        import math

        dist = math.sqrt( x**2 + y**2 )

        # if we're below treshold_min, or if we were below treshold
        # and didn't go enough above treshold_max
        if dist < self.treshold_min or dist < self.treshold_max and self.prev_angle is None:
            self.prev_angle = None
            return 0

        # if we just went above treshold_max
        if self.prev_angle is None:
            self.prev_angle = self.base_angle = get_angle( x, y )
            self.rotations_offset_angle = 0
            return 0

        # if we were and still are above tresholds
        angle = get_angle( x, y )

        if self.prev_angle > 0 and angle < 0 and self.prev_angle - angle > angle+360 - self.prev_angle:
            self.rotations_offset_angle += 360

        if self.prev_angle < 0 and angle > 0 and angle - self.prev_angle > self.prev_angle - (angle-360):
            self.rotations_offset_angle -= 360

        self.prev_angle = angle

        final_angle = angle + self.rotations_offset_angle - self.base_angle
        if final_angle > self.max_angle:
            final_angle = self.max_angle
        elif final_angle < -self.max_angle:
            final_angle = -self.max_angle

        if dist > self.treshold_max:
            return final_angle / self.max_angle
        else:
            return final_angle / self.max_angle * ( ( dist-self.treshold_min ) / ( self.treshold_max - self.treshold_min ) )


def stick_axes_into_one_axis( x, y, turn_max, tresh_min, tresh_max ):
    """Maps two axes from a stick into one axis.
    If you turn stick turn_max degrees to the left - result is -1.
    if you turn stick turn_max degrees to the right - result is +1.
    If distance from center to stick position is less than tresh_min - result is 0.
    If that distance is between tresh_min and tresh_max - result is somewhere between 0 and value
    corresponding to current turn of the stick, depending how far that distance is from the center.
    If that distance is more than tresh_max - result is full value of the current turn.
    """

    if x == 0:
        return 0

    import math

    dist = math.sqrt( x**2 + y**2 )

    if dist <= tresh_min:
        return 0

    turn_angle = get_angle( x, y )

    if turn_angle > turn_max:
        turn_angle = turn_max
    elif turn_angle < -turn_max:
        turn_angle = -turn_max

    if dist >= tresh_max:
        return turn_angle / turn_max
    else:
        return turn_angle / turn_max * ( (dist-tresh_min) / (tresh_max-tresh_min) )

class LogitechF310Input( UserInput ):
    def __init__( self ):
        import pygame
        for i in range( pygame.joystick.get_count( ) ):
            self.joy = pygame.joystick.Joystick( i )
            if self.joy.get_name( ) == "Controller (Gamepad F310)":
                self.joy.init( )
                return
        else:
            raise InputDeviceUnavailable( "Logitech F310 gamepad could not be found" )

    def get_steering( self ):
        return self.joy.get_axis( 0 ) ** 2

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

class MouseInput( UserInput ):
    def __init__( self ):
        self.center = 200, 200
        self.last_pos = 0, 0

        self.angler = StickAngle( 720, 50, 100 )

    def get_steering( self ):
        #return stick_axes_into_one_axis( self.last_pos[0]-self.center[0],
        #                                 self.last_pos[1]-self.center[1],
        #                                 135, 40, 80 )
        return self.angler.update_angle( self.last_pos[0]-self.center[0],
                                         self.last_pos[1]-self.center[1] )

    def get_throttle( self ):
        return 0

    def get_brake( self ):
        return 0

    def process_pygame_event( self, event ):
        import pygame

        if event.type == pygame.MOUSEMOTION:
            self.last_pos = event.pos
            return True

        return False

class LogitechFormulaForceEXInput( UserInput ):
        def __init__( self ):
            import pygame
            for i in range( pygame.joystick.get_count( ) ):
                self.joy = pygame.joystick.Joystick( i )
                if self.joy.get_name( ) == "Logitech Formula Force EX USB":
                    self.joy.init( )
                    return
            else:
                raise InputDeviceUnavailable( "Logitech Formula Force EX USB racing wheel could not be found" )

        def get_steering( self ):
            return self.joy.get_axis( 0 ) ** 2

        def get_throttle( self ):
            return round( (self.joy.get_axis( 2 ) - 1) / -2, 2 )

        def get_brake( self ):
            return round( (self.joy.get_axis( 3 ) - 1) / -2, 2 )

        def process_pygame_event( self, event ):
            return False

class LogitechFormulaForceRXInput( UserInput ):
        def __init__( self ):
            import pygame
            for i in range( pygame.joystick.get_count( ) ):
                self.joy = pygame.joystick.Joystick( i )
                if self.joy.get_name( ) == "Logitech Formula Force RX":
                    self.joy.init( )
                    return
            else:
                raise InputDeviceUnavailable( "Logitech Formula Force RX racing wheel could not be found" )

        def get_steering( self ):
            return self.joy.get_axis( 0 ) ** 2

        def get_throttle( self ):
            axis = self.joy.get_axis( 1 )
            return round( -axis if axis<0 else 0, 2 )

        def get_brake( self ):
            axis = self.joy.get_axis( 1 )
            return round( axis if axis>0 else 0, 2 )

        def process_pygame_event( self, event ):
            return False

def get_available_input( ):
    input_classes = ( LogitechFormulaForceRXInput,
                      LogitechFormulaForceEXInput,
                      LogitechF310Input )

    for possible_input in input_classes:
        try:
            initialized_input = possible_input( )
            break
        except InputDeviceUnavailable:
            continue
    else:
        # initialized_input = KeyboardInput( )
        initialized_input = MouseInput( )

    return initialized_input

if __name__ == "__main__":
    print( "contains input devices classes, should be used as a module" )
