import flask

def findall( string, substring ):
	result = []

	found_at = string.find( substring )
	while found_at != -1:
		result.append( found_at )
		found_at += len( substring )
		found_at = string.find( substring, found_at )

	return result

def emphasize( string, positions, open, close ):
	shift = 0
	shift_increase = len( open ) + len( close )
	for position in positions:
		string = string[ : position[0] + shift ] + open + string[ position[0] + shift : position[1] + shift ] + close + string[ position[1] + shift : ]
		shift += shift_increase

	return string

def emphasize2( string, positions ):
	emphasized = []
	previous_start = 0
	for position in positions:
		emphasized.append( { "text" : string[ previous_start : position[0] ], "bold" : False } )
		emphasized.append( { "text" : string[ position[0] : position[1] ], "bold" : True } )
		previous_start = position[1]

	emphasized.append( { "text" : string[ previous_start : ], "bold" : False } )
	
	return emphasized

app = flask.Flask( __name__ )

@app.route( "/", methods=['GET', 'POST'] )
@app.route( "/search", methods=['GET', 'POST'] )
def search( ):
	if flask.request.method == 'GET':
		return flask.render_template( "search.html" )
	else:
		all_files = { f : flask.request.files[ f ].stream.read( ).decode( ).split( "\n" )
					  for f in flask.request.files }
		what = flask.request.form[ "what" ]
		results = {}
		emphasized_files = {}

		for filename in all_files:
			results[ filename ] = []
			emphasized_files[ filename ] = []
			for n, line in zip( range( len( all_files[ filename ] ) ), all_files[ filename ] ):
				line_results = findall( line, what )
				emphasized_files[ filename ].append( emphasize2( line, [ ( start_position, start_position + len( what ) ) for start_position in line_results ] ) )

				#if line_results:
				#	results[ filename ] += [ ( n, line_results ) ]
				#	emphasized_files[ filename ].append( emphasize( line, [ ( start_position, start_position + len( what ) ) for start_position in line_results ], "<strong>", "</strong>" ) )
				#else:
				#	emphasized_files[ filename ].append( line )

		return flask.render_template( "result.html", url_args=dict( flask.request.args ), form=dict( flask.request.form ), files=all_files, search_result=emphasized_files )			
