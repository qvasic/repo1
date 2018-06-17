def position_polyline( polyline, orient=(0,-1), posit=(0,0) ):
    import pygame.math
    angle = -pygame.math.Vector2( orient ).angle_to( (0, -1) )
    return [ [ rot+rel for rot, rel in zip( pygame.math.Vector2( p ).rotate( angle ), posit ) ]
             for p in polyline ]

def rotate_vec( vec, orient, posit=(0,0) ):
    import pygame.math
    angle = -pygame.math.Vector2( orient ).angle_to( (0, -1) )
    return tuple( r+p for r, p in zip( pygame.math.Vector2( vec ).rotate( angle ), posit ) )

def length( v ):
    """Return length of the vector v."""
    import math
    return math.sqrt( v[0]**2 + v[1]**2 )

def redirect_vec( v_from, v_to ):
    """Redirects vector v_from in the direction of v_to.
    Basically it builds new vector of length of v_from in the direction v_to."""
    coef = length( v_from )/length( v_to )
    return [ c*coef for c in v_to ]
