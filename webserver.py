import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
	if 'email' in flask.session:
		return "welcome %s" % (flask.session['email'])
	else:
		return "please login or register"

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')

