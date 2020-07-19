import flask

app = flask.Flask( __name__ )

@app.route( "/", methods=['GET', 'POST'] )
@app.route( "/search", methods=['GET', 'POST'] )
def hell0( ):
	if flask.request.method == 'GET':
		return flask.render_template( "search.html" )
	else:
		all_files = { f : ( flask.request.files[ f ].content_type, 
		                    flask.request.files[ f ].stream.read( ) ) 
						for f in flask.request.files }
			
		return "search result will be here, url args: {} form: {}, files: {}".format( dict( flask.request.args ), 
																					  dict( flask.request.form ),
																					  all_files )
