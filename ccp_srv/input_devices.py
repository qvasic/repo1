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
        pygame.key.set_repeat( 300, 150 )

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

def dead_center( value, gravity ):
    """Maps value in a way, that everything between -gravity to +gravity becomes 0.
    Everything else from -1 to -gravity and from +gravity to +1 becomes one continuous gradient
    from -1 to +1."""

    if -gravity <= value and value <= gravity:
        return 0
    else:
        value -= gravity if value>0 else -gravity
        return value / (1-gravity)

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
        return round( dead_center( self.joy.get_axis( 0 ), 0.05 ), 2 )

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
            return round( dead_center( self.joy.get_axis( 0 ), 0.05 ), 2 )

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
            return round( dead_center( self.joy.get_axis( 0 ), 0.05 ), 2 )

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
        initialized_input = KeyboardInput( )

    return initialized_input

if __name__ == "__main__":
    print( "contains input devices classes, should be used as a module" )
