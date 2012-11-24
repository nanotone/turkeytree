import subprocess


EXIF_KEYS = (
	('Exposure Time', 'exposure'),
	('ISO Speed Ratings', 'iso'),
	('F-Number', 'aperture'),
	('Date and Time (Original)', 'time'),
	('GPS Time (Atomic Clock)', 'gpstime'),
	('Orientation', 'orientation'),
)


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

def is_jpeg(path):
	try:
		return 'JPEG image data' in subprocess.check_output(['file', path], universal_newlines=True)
	except subprocess.CalledProcessError:
		pass
	return False

def thumbnailize(src, dst):
	subprocess.check_call(['convert', src, '-resize', '200x200>', dst])
