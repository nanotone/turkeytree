import calendar
import re
import subprocess
import time


EXIF_KEYS = (
	('Exposure Time', 'exposure'),
	('ISO Speed Ratings', 'iso'),
	('F-Number', 'aperture'),
	('Date and Time (Original)', 'time'),
	('GPS Time (Atomic Clock)', 'gpstime'),
	('Orientation', 'orientation'),
	('Model', 'model'),
)


def _parse_time(s):
	try:
		return calendar.timegm(time.strptime(s, '%Y:%m:%d %H:%M:%S'))
	except ValueError:
		return None

def auto_orient(src, dst):
	subprocess.check_call(['exiftran', '-a', '-o', dst, src])

def get_dimensions(path):
	return map(int, subprocess.check_output(['identify', path], universal_newlines=True).split()[2].split('x'))

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

def get_tzoned_time(exif):
	# N.B.: a NAIVE TIME is a tz-less clock moment, encoded using epoch-seconds
	# as if the clock were in UTC. Real UTC-time is incidental knowledge, which
	# can be calculated if the optional tzoffset field is available.
	naive_str = exif.get('time', "")
	naive_time = _parse_time(naive_str)
	if not naive_time:
		return None
	# Now we try to use GPS time to calculate UTC+tzoffset
	utc_str = exif.get('gpstime')
	if utc_str:
		# First, strip fractional seconds off end
		match = re.match(r'([\d\s:]+)\.\d*$', utc_str)
		if match:
			utc_str = match.group(1)
		# Try parsing absolute time first
		utc_time = _parse_time(utc_str)
		if utc_time:
			utc_time = int(round((utc_time - naive_time) / 900.0)) * 900 + naive_time  # round to nearest 15-min
			return {'naive': utc_time, 'tzoffset': naive_time - utc_time}
		# Next, try parsing relative time-of-day
		utc_time = _parse_time(naive_str[:11] + utc_str)
		if utc_time:
			utc_time = int(round((utc_time - naive_time) / 900.0)) * 900 + naive_time  # round to nearest 15-min
			while naive_time - utc_time <= -40500: naive_time += 24*3600  # min UTC-11.25
			while naive_time - utc_time >   45900: naive_time -= 24*3600  # max UTC+12.75 inclusive
			return {'naive': naive_time, 'tzoffset': naive_time - utc_time}
	# Failed to get UTC+tzoffset, so return naively
	return {'naive': naive_time, 'tzoffset': None}


def is_jpeg(path):
	try:
		return 'JPEG image data' in subprocess.check_output(['file', path], universal_newlines=True)
	except subprocess.CalledProcessError:
		pass
	return False

def thumbnailize(src, dst):
	subprocess.check_call(['convert', src, '-resize', '200x200>', dst])
