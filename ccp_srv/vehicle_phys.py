import earth_walk

class VehicleOnEarthSurface:
    def __init__( self ):
        # position
        self.lat = 0
        self.lng = 0
        self.bearing = 0

        # geometry
        self.wheelbase_m = 4
        self.max_front_turn_deg = 50

        # intertia and propulsion
        self.mass_kg = 2000
        self.speed_m_s = 0

        self.max_thrust_n = 1000
        self.internal_friction_n = 100
        self.drag_coefitient = 0.5
        self.max_braking_n = 300

    def move( self, time_s, steering, throttle, brake ):
        """Moves vehicle.
        time_s - seconds for how long to move the vehicle, float
        steering - float from -1 to 1, negative - left, positive - right
        throttle - float from 0 to 1
        brake - float from 0 1"""

        import math

        forces_combined_n = ( self.max_thrust_n * throttle
                            - self.internal_friction_n
                            - self.drag_coefitient * self.speed_m_s
                            - self.max_braking_n * brake )

        acceleration_m_s_2 = forces_combined_n / self.mass_kg

        self.speed_m_s += acceleration_m_s_2 * time_s
        if self.speed_m_s < 0:
            self.speed_m_s = 0

        dist_traveled_m = self.speed_m_s * time_s

        turn_radius = ( math.tan( earth_walk.deg_to_rad( self.max_from_turn_deg * abs( steering ) ) )
                            * self.wheelbase_m )
