#!/usr/bin/env python

import os

if __name__ == '__main__':
	try:
		os.mkdir('static/upload')
	except OSError:
		pass

	with open('secret_key', 'w') as f:
		f.write(os.urandom(24))
