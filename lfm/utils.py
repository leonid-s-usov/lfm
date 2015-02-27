import contextlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import urllib2

import yaml


CONFIG = '.lambda.yml'


class LfmException(Exception):
	pass


########################################
# COMPATIBILITY
########################################

PY2 = sys.version_info[0] == 2

def iteritems(d):
	return d.iteritems() if PY2 else d.items()


########################################
# DIRECTORY/FILE UTILS
########################################

def normalize_path(path):
	return path.replace('/', os.sep)

@contextlib.contextmanager
def directory(path):
	'''Context manager for changing the current working directory'''
	path = normalize_path(path)
	if not os.path.isdir(path):
		raise IOError('"{}" is not a valid directory!'.format(path))
	prev_cwd = os.getcwd()
	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(prev_cwd)

def load_config():
	if not os.path.isfile(CONFIG):
		return {
			'config': {},
			'ignore': []
		}
	with open(CONFIG, 'r') as f:
		return yaml.load(f)

def delete_resource(path):
	path = normalize_path(path)
	if os.path.isfile(path):
		os.remove(path)
	elif os.path.isdir(path):
		shutil.rmtree(path, ignore_errors=True)

def make_zip(name):
	# Due to a bug in make_archive, root_dir still has to be specified
	shutil.make_archive(name, format='zip', root_dir=os.getcwd())


########################################
# SHELL
########################################

def shell(command):
	return subprocess.call(shlex.split(command))


########################################
# GIST
########################################

# Returns a list of files in the Gist
def download_gist(gid, dest):
	req = urllib2.Request('https://api.github.com/gists/{}'.format(gid))
	res = json.loads(urllib2.urlopen(req).read())
	ret = []
	for k, v in iteritems(res['files']):
		ret.append(k)
		with open(os.path.join(dest, k), 'w') as f:
			f.write(v['content'])
	return ret
