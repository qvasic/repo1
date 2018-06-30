import earth_walk

class VehicleOnEarthSurface:
    def __init__( self ):
        # position
        self.lat = 0
        self.lng = 0
        self.bearing_deg = 0

        # geometry
        self.wheelbase_m = 4
        self.max_front_turn_deg = 50

        # intertia and propulsion
        self.mass_kg = 2000
        self.speed_m_s = 0

        self.max_thrust_n = 10000
        self.internal_friction_n = 700
        self.drag_compontents = 3
        self.max_braking_n = 12000

    def recalc_speed( self, time_s, throttle_ctrl, brake_ctrl ):
        """Recalculate speed change over time.
        times_s - float, time over which speed must be recalculated,
        throttle_ctrl - input from user, float 0 to 1, indicates how much acceleration is applied
        brake_ctrl - input from user, float 0 to 1, indicates how much braking is applied"""

        forces_combined_n = ( self.max_thrust_n * throttle_ctrl
                            - self.internal_friction_n
                            - self.drag_compontents * self.speed_m_s**2
                            - self.max_braking_n * brake_ctrl )

        acceleration_m_s_2 = forces_combined_n / self.mass_kg
        self.speed_m_s += acceleration_m_s_2 * time_s

        if self.speed_m_s < 0:
            self.speed_m_s = 0

    def move_straight( self, dist_m ):
        """Recalc vehicle position by moving it straight by dist_m meters."""

        import earth_walk

        prev_lat, prev_lng = self.lat, self.lng
        self.lat, self.lng = earth_walk.step( self.lat, self.lng, self.bearing_deg,
                            earth_walk.Earth_dist_to_deg( dist_m ) )
        self.bearing_deg = (
            (earth_walk.dist_and_brng( self.lat, self.lng, prev_lat, prev_lng )[1]+180) % 360
        )

    def move_curved( self, dist_m, steering_ctrl ):
        """Recalc vehicle position by moving it by dist_m meters
        taking into account steering input from user.
        Assumes that each movement operation is relatively small,
        otherwise this methematical model is not quite right."""

        import math, earth_walk

        back_wheel_to_turn_center_m = (
            math.tan( earth_walk.deg_to_rad( 90 - self.max_front_turn_deg * abs( steering_ctrl ) ) )
            * self.wheelbase_m
        )
        turn_radius_m = math.sqrt( ( back_wheel_to_turn_center_m )**2
                                   + (self.wheelbase_m/2)**2 )
        angle_turned_rad = dist_m / turn_radius_m
        if angle_turned_rad > math.pi/2:
            raise ValueError( "Speed is too fast for this turn radius." )

        direct_dist_to_end_of_travel_m = 2 * turn_radius_m * math.sin( angle_turned_rad/2 )
        direct_bearing_to_end_of_travel_deg = 90 - angle_turned_rad/2

        steer_dir = 1 if steering_ctrl > 0 else -1

        new_lat, new_lng = earth_walk.step( self.lat, self.lng,
                            self.bearing_deg + steer_dir * direct_bearing_to_end_of_travel_deg,
                            earth_walk.Earth_dist_to_deg( direct_dist_to_end_of_travel_m ) )

        new_bearing_deg = ( earth_walk.dist_and_brng( new_lat, new_lng, self.lat, self.lng )[1]+180
                            - steer_dir * direct_bearing_to_end_of_travel_deg
                            + steer_dir * earth_walk.rad_to_deg( angle_turned_rad )
                          ) % 360

        self.lat, self.lng, self.bearing_deg = new_lat, new_lng, new_bearing_deg


    def move( self, time_s, steering_ctrl, throttle_ctrl, brake_ctrl ):
        """Moves vehicle.
        time_s - seconds for how long to move the vehicle, float
        steering - float from -1 to 1, negative - left, positive - right
        throttle - float from 0 to 1
        brake - float from 0 to 1"""

        self.recalc_speed( time_s, throttle_ctrl, brake_ctrl )

        if self.speed_m_s > 0:
            dist_traveled_m = self.speed_m_s * time_s
            if steering_ctrl != 0:
                self.move_curved( dist_traveled_m, steering_ctrl )
            else:
                self.move_straight( dist_traveled_m )

def selftest():
    print( "performing smoke self-testing" )

    v = VehicleOnEarthSurface()
    assert v.lat == 0 and v.lng == 0 and v.speed_m_s == 0

    v.move( 1, 0, 0, 0 )
    assert v.lat == 0 and v.lng == 0 and v.speed_m_s == 0

    v.move( 1, 0, 1, 0 )
    assert v.lat > 0 and round( v.lng, 19 ) == 0 and v.speed_m_s > 0

    v.move( 1, 0.3, 1, 0 )
    assert v.lat > 0 and v.lng > 0 and v.speed_m_s > 0

if __name__ == "__main__":
    selftest()
