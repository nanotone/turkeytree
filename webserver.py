import functools

import bson
import flask
import pymongo

app = flask.Flask(__name__)

db = pymongo.Connection().turkeytree


def auth(required=True):
	def decorator(f):
		@functools.wraps(f)
		def wrapper(*args, **kwargs):
			try:
				user = db.users.find_one({'_id': bson.ObjectId(flask.session['userid'])})
				assert user
				kwargs['user'] = user
			except (AssertionError, KeyError, bson.errors.InvalidId):
				if required:
					return flask.render_template('login.html')
				kwargs['user'] = None
			return f(*args, **kwargs)
		return wrapper
	return decorator


@app.route('/')
@auth(required=False)
def index(user):
	if user:
		return flask.render_template('home.html', user=user)
	else:
		return flask.render_template('index.html')

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

@app.route('/album', methods=['POST'])
@auth(required=True)
def album_create(user):
	form = flask.request.form
	if not form['name']:
		return flask.render_template('home.html', user=user)
	doc = {'name': form['name'], 'owner': user['_id']}
	db.albums.insert(doc, safe=True)
	albumid = str(doc['_id'])
	return flask.redirect(flask.url_for('album', albumid=albumid))

@app.route('/album/<albumid>')
@auth(required=True)
def album(albumid, user):
	try:
		album = db.albums.find_one({'_id': bson.ObjectId(albumid)})
		return "there are probably no events in this album"
	except bson.errors.InvalidId:
		return "album not found"

if __name__ == '__main__':
	app.secret_key = open('secret_key').read()
	app.run(debug=True, host='0.0.0.0')

