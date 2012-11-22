import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
	if 'userid' in flask.session:
		return "welcome %s" % (flask.session['userid'])
	else:
		return flask.render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
	form = flask.request.form
	if form['email'] == "let@me.in" and form['password'] == "letmein":
		flask.session['userid'] = "hello"
		return flask.redirect(flask.url_for('index'))
	else:
		return flask.render_template('login.html')

if __name__ == '__main__':
	app.secret_key = open('secret_key').read()
	app.run(debug=True, host='0.0.0.0')

