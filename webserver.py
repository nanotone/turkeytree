import functools
import json
import subprocess
import time

import bson
import flask
import pymongo


EXIF_KEYS = (
	('Exposure Time', 'exposure'),
	('ISO Speed Ratings', 'iso'),
	('F-Number', 'aperture'),
	('Date and Time (Original)', 'time'),
	('GPS Time (Atomic Clock)', 'gpstime'),
	('Orientation', 'orientation'),
)


app = flask.Flask(__name__)

db = pymongo.Connection().turkeytree


def get_exif(path):
	try:
		exif = subprocess.check_output(['exif', '-m', path], universal_newlines=True)
		exif = dict(line.split('\t')[:2] for line in exif.split('\n') if '\t' in line)
		print(exif)
		exif = {k2: exif[k1] for k1, k2 in EXIF_KEYS}
		print(exif)
		return exif
	except subprocess.CalledProcessError:
		return None

def get_dimensions(path):
	return map(int, subprocess.check_output(['identify', path], universal_newlines=True).split()[2].split('x'))


def is_jpeg(path):
	try:
		return 'JPEG image data' in subprocess.check_output(['file', path], universal_newlines=True)
	except subprocess.CalledProcessError:
		pass
	return False

class JSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bson.ObjectId):
			return str(obj)
		return json.JSONEncoder.default(self, obj)
json_encoder = JSONEncoder()

def auth(required=True):
	def decorator(f):
		@functools.wraps(f)
		def wrapper(*args, **kwargs):
			try:
				user = kwargs.get('user')
				if not user:
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
		albums = list(db.albums.find({'owner': user['_id']}))
		return flask.render_template('home.html', user=user, albums=albums)
	else:
		return flask.render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'POST':
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
		flask.flash('album name is required', category='album_creation_error')
		return flask.redirect(flask.url_for('index'))
	doc = {'name': form['name'], 'owner': user['_id']}
	db.albums.insert(doc, safe=True)
	albumid = str(doc['_id'])
	return flask.redirect(flask.url_for('album', albumid=albumid))

@app.route('/album/<albumid>')
@auth(required=True)
def album(albumid, user):
	try:
		album = db.albums.find_one({'_id': bson.ObjectId(albumid)})
		assert album
		return flask.render_template('album.html', album=album, user=user)
	except (AssertionError, bson.errors.InvalidId):
		return "album not found"

@app.route('/album/<albumid>/upload')
@auth(required=True)
def album_upload(albumid, user):
	try:
		album = db.albums.find_one({'_id': bson.ObjectId(albumid)})
		assert album
		return flask.render_template('upload.html', album=album, user=user)
	except (AssertionError, bson.errors.InvalidId):
		return "album not found"

@app.route('/photo', methods=['POST'])
@auth(required=True)
def photo_create(user):
	photo = flask.request.files.get('photo')
	if not photo or photo.filename.split('.')[-1].lower() not in ('jpg', 'jpeg'):
		return "not jpeg"
	doc = {'time': time.time()}
	doc['_id'] = fileid = bson.ObjectId()
	doc['original_path'] = doc['path'] = path = 'static/upload/%s.jpg' % (fileid)
	photo.save(path)
	if not is_jpeg(path):
		return "not jpeg"
	#sha1 = subprocess.check_output(['sha1sum', path], universal_newlines=True).split()[0]
	#doc['sha1'] = sha1
	exif = get_exif(path)
	if exif and exif.get('orientation') != 'Top-left':
		doc['path'] = 'static/upload/%s_rotated.jpg' % (fileid)
		subprocess.check_call(['exiftran', '-a', '-o', doc['path'], path])
		path = doc['path']
	doc['tn'] = 'static/upload/%s_tn.jpg' % (fileid)
	subprocess.check_call(['convert', path, '-resize', '200x200>', doc['tn']])
	doc['tn_size'] = get_dimensions(doc['tn'])
	return json_encoder.encode(doc)

if __name__ == '__main__':
	app.secret_key = open('secret_key').read()
	app.run(debug=True, host='0.0.0.0')

