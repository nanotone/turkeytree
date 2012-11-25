import functools
import json
import subprocess
import time

import bson
import flask
import pymongo

import imglib


app = flask.Flask(__name__)

def get_db():
	db = getattr(flask.g, 'db', None)
	if not db:
		flask.g.db = db = pymongo.Connection().turkeytree
	return db


class JSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bson.ObjectId):
			return str(obj)
		return json.JSONEncoder.default(self, obj)

def render_template(template_name, **kwargs):
	kwargs['user'] = getattr(flask.g, 'user', None)
	return flask.render_template(template_name + '.html', **kwargs)

def auth(required=True):
	def decorator(f):
		@functools.wraps(f)
		def wrapper(*args, **kwargs):
			flask.g.user = None
			try:
				user = get_db().users.find_one({'_id': bson.ObjectId(flask.session['userid'])})
				assert user
				flask.g.user = user
			except (AssertionError, KeyError, bson.errors.InvalidId):
				if required:
					return render_template('login')
			return f(*args, **kwargs)
		return wrapper
	return decorator

def get_album(albumid):
	try:
		return get_db().albums.find_one({'_id': bson.ObjectId(albumid)})
	except (AssertionError, bson.errors.InvalidId):
		return None

@app.template_filter('jsonify')
def jsonify(doc):
	return JSONEncoder().encode(doc)


@app.route('/')
@auth(required=False)
def index():
	if flask.g.user:
		albums = list(get_db().albums.find({'owner': flask.g.user['_id']}))
		return render_template('home', albums=albums)
	else:
		return render_template('index')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'POST':
		form = flask.request.form
		try:
			user = get_db().users.find_one({'email': form['email'], 'password': form['password']})
			if user:
				flask.session['userid'] = str(user['_id'])
				return flask.redirect(flask.url_for('index'))
		except KeyError:
			pass
	return render_template('login')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if flask.request.method == 'GET':
		return render_template('register')
	elif flask.request.method == 'POST':
		form = flask.request.form
		doc = {'email': form['email'], 'password': form['password']}
		try:
			get_db().users.insert(doc, safe=True)
		except pymongo.errors.DuplicateKeyError:
			return "that email already exists"
		flask.session['userid'] = str(doc['_id'])
		return flask.redirect(flask.url_for('index'))

@app.route('/logout')
def logout():
	flask.session.pop('userid', None)
	return flask.redirect(flask.url_for('index'))

@app.route('/album', methods=['POST'])
@auth(required=True)
def album_create():
	form = flask.request.form
	if not form['name']:
		flask.flash('album name is required', category='album_creation_error')
		return flask.redirect(flask.url_for('index'))
	doc = {'name': form['name'], 'owner': flask.g.user['_id'], 'photos': []}
	get_db().albums.insert(doc, safe=True)
	albumid = str(doc['_id'])
	return flask.redirect(flask.url_for('album', albumid=albumid))

@app.route('/album/<albumid>')
@auth(required=True)
def album(albumid):
	album = get_album(albumid)
	if not album:
		return "album not found"
	photos = list(get_db().photos.find({'_id': {'$in': album.get('photos', [])}}))
	return render_template('album', album=album, photos=photos)

@app.route('/album/<albumid>/upload', methods=['GET', 'POST'])
@auth(required=True)
def album_upload(albumid):
	album = get_album(albumid)
	if not album:
		return "album not found"
	if flask.request.method == 'GET':
		return render_template('upload', album=album)
	else:
		form = flask.request.form
		try:
			fileids = list(map(bson.ObjectId, set(form.get('fileids', '').strip().split())))
			if fileids and get_db().photos.find({'_id': {'$in': fileids}}).count() == len(fileids):
				get_db().albums.update({'_id': album['_id']}, {'$pushAll': {'photos': fileids}})
		except Exception:
			pass  # inform the user
		return flask.redirect(flask.url_for('album', albumid=albumid))

@app.route('/photo', methods=['POST'])
@auth(required=True)
def photo_create():
	photo = flask.request.files.get('photo')
	if not photo or photo.filename.split('.')[-1].lower() not in ('jpg', 'jpeg'):
		return "not jpeg"
	doc = {'created': time.time()}
	doc['_id'] = fileid = bson.ObjectId()
	doc['original_path'] = doc['path'] = path = 'static/upload/%s.jpg' % (fileid)
	photo.save(path)
	if not imglib.is_jpeg(path):
		return "not jpeg"

	#sha1 = subprocess.check_output(['sha1sum', path], universal_newlines=True).split()[0]
	#doc['sha1'] = sha1
	exif = imglib.get_exif(path)
	if exif:
		if exif.get('orientation') != 'Top-left':
			doc['path'] = 'static/upload/%s_rotated.jpg' % (fileid)
			imglib.auto_orient(path, doc['path'])
			path = doc['path']
		tzoned_time = imglib.get_tzoned_time(exif)
		if tzoned_time:
			doc['time'] = tzoned_time

	doc['tn'] = 'static/upload/%s_tn.jpg' % (fileid)
	imglib.thumbnailize(path, doc['tn'])
	doc['tn_size'] = imglib.get_dimensions(doc['tn'])
	get_db().photos.save(doc)
	return jsonify(doc)

if __name__ == '__main__':
	app.secret_key = open('secret_key').read()
	app.run(debug=True, host='0.0.0.0')

