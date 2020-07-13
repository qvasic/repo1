import flask

app = flask.Flask( __name__ )

@app.route( "/", methods=['GET', 'POST'] )
@app.route( "/search", methods=['GET', 'POST'] )
def hell0( ):
	if flask.request.method == 'GET':
		return flask.render_template( "search.html" )
	else:
		return "search result will be here, url args: {} form: {}, files: {}".format( len( flask.request.args ), 
																					  len( flask.request.form ),
																					  len( flask.request.files ) )
