import bson
import flask
import pymongo

app = flask.Flask(__name__)

db = pymongo.Connection().turkeytree


@app.route('/')
def index():
	try:
		user = db.users.find_one({'_id': bson.ObjectId(flask.session['userid'])})
		assert user
		return flask.render_template('index.html', user=user)
	except (KeyError, bson.errors.InvalidId):
		pass

	return flask.render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
	form = flask.request.form
	try:
		user = db.users.find_one({'email': form['email'], 'password': form['password']})
		if user:
			flask.session['userid'] = str(user['_id'])
			return flask.redirect(flask.url_for('index'))
	except KeyError:
		pass
	return flask.render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if flask.request.method == 'GET':
		return flask.render_template('register.html')
	elif flask.request.method == 'POST':
		form = flask.request.form
		doc = {'email': form['email'], 'password': form['password']}
		try:
			db.users.insert(doc, safe=True)
		except pymongo.errors.DuplicateKeyError:
			return "that email already exists"
		flask.session['userid'] = str(doc['_id'])
		return flask.redirect(flask.url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
	flask.session.pop('userid', None)
	return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
	app.secret_key = open('secret_key').read()
	app.run(debug=True, host='0.0.0.0')

