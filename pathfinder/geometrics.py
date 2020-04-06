import math

def rad_to_deg( r ):
    """Converts radians to degress."""
    return r / ( math.pi/180 )

def deg_to_rad( d ):
    """Converts degrees to radiands."""
    return d * ( math.pi/180 )

def angle( x, y ):
    """Returns angle in degrees between line (0,0)-(x,y) and positive direction of axis X.
    Returned value can be [0, 360)."""

    if x==0:
        if y==0:
            raise ValueError( "No angle can be computed: (0,0)-(0,0) does not define a line." )
        else:
            return 90 if y>0 else 270

    a = rad_to_deg( math.atan( y/x ) )
    if x<0:
        return 180+a
    elif y<0:
        return 360+a
    else:
        return a

def length( x, y ):
    """Returns length of vector (0,0)-(x,y)."""
    return math.sqrt( x**2 + y**2 )

def coords( a, l ):
    """Returns tuple with coordinates of the point, which is located at distance l from origin,
    and at l degrees of angle relative positive direction of axis X."""

    x = math.cos( deg_to_rad( a ) ) * l
    y = math.sin( deg_to_rad( a ) ) * l
    return x, y

def rotate( x, y, a ):
    """Returns coordinates x,y rotated by a degrees around origin.
    Positive a means rotation clockwise, negative - counterclockwise."""
    return coords( angle( x, y )+a, length( x, y ) )
