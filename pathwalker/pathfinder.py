def find_smallest_by_value( container, get_value = lambda x : x ):
    """Returns key with the smallest value, or None if no elements."""
    key_with_smallest_value = None
    for key in container:
        if key_with_smallest_value is None or get_value( container[key_with_smallest_value] ) > get_value( container[key] ):
            key_with_smallest_value = key
    return key_with_smallest_value

def find_cheapest_path_dijkstra( graph, start_id, end_id ):
    visited = dict( )
    tentative = { start_id : { "cost" : 0, "from" : None } }

    while len( tentative ) > 0:
        current_tentative = find_smallest_by_value( tentative, lambda x : x["cost"] )

        if current_tentative == end_id:
            backtrack = [ end_id, tentative[ end_id ][ "from" ] ]
            while backtrack[ -1 ] != start_id:
                backtrack.append( visited[ backtrack[ -1 ] ][ "from" ] )

            return { "cost" : tentative[ current_tentative ][ "cost" ], "path" : list( reversed( backtrack ) ) }

        for connected in graph[ current_tentative ]:
            if connected in visited:
                continue

            dist_throught_current_tentative = tentative[ current_tentative ][ "cost" ] + graph[ current_tentative ][ connected ]
            if connected not in tentative or tentative[ connected ][ "cost" ] > dist_throught_current_tentative:
                tentative[connected] = { "cost" : dist_throught_current_tentative, "from" : current_tentative }

        visited[ current_tentative ] = tentative[ current_tentative ]
        del tentative[ current_tentative ]

    return None
