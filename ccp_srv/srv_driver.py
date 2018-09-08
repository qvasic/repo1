def main( ):
    import srv, sys
    from vehicle_driver import VehicleDriver

    start_coords = None

    try:
        if len( sys.argv ) == 2:
            start_coords = list( map( float, sys.argv[1].split( "," ) ) )
        elif len( sys.argv ) >= 3:
            start_coords = list( map( float, sys.argv[1:3] ) )
        if start_coords and ( start_coords[0] > 90 or start_coords[0] < -90 or start_coords[1] > 180 or start_coords[1] < -180 ):
            raise ValueError( "Coordinates are out of possible bounds." )
    except ValueError:
        print( "INIT start coordinates are invalid, using default ones" )
        start_coords = None

    shared_bin_nmea = srv.SharedData( b"" )

    def update_coords_shared( lat, lng, speed_m_s, bearing ):
        import nmea
        nmea_sents = nmea.gpgga_gpgsa_gprmc( lat, lng, nmea.meters_to_knots( 3600*speed_m_s ),
                                             bearing ).encode( "utf-8" )
        shared_bin_nmea.set( nmea_sents )


    server = srv.CCPServer( shared_bin_nmea )
    server.start( )

    d = VehicleDriver( update_coords_shared )
    d.run( start_coords )

    server.stop( )

if __name__ == "__main__":
    main( )
