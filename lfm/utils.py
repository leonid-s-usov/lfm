import contextlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import urllib2

import boto3
import yaml


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


########################################
# S3
########################################

# Returns a list of files downloaded
def download_s3(path, dest):
	ret = []
	bucket, subpath = path.split('/', 1) if '/' in path else (path, '')
	for e in boto3.resource('s3').Bucket(bucket).objects.all():
		if e.key.startswith(subpath):
			if e.key != subpath:
				resource = e.key.replace(subpath, '', 1)
				# Strip leading slash, if any
				if resource.startswith('/'):
					resource = resource[1:]
			else:
				resource = e.key
			ret.append(resource)
			body = e.get()['Body']
			with open(os.path.join(dest, resource), 'wb') as f:
				for chunk in iter(lambda: body.read(4096), b''):
					f.write(chunk)
	return ret


########################################
# FRONT MATTER PARSING
########################################

# Hey I know, let's parse comments with REGEX! That'll be fun!
#   - No one, ever (and yet here we are...)
regexes = {
	'js': re.compile('\s*(\/\*([\S\s]*?)\*\/|(\/\/(.+?)$\s)*)', re.MULTILINE),
	'coffee': re.compile('\s*((#(.+?)$\s)*)', re.MULTILINE),
}

def find_front_matter(s, ext):
	if ext not in regexes:
		return ''
	return re.search(regexes[ext], s).group().strip()

def parse_front_matter(s, ext):
	def parse_fm_line(line):
		line = re.sub('(\/\*|\*\/)', '', line)  # Remove /*, */
		return re.sub('(\/\/|\*|#)', '', line, count=1)  # Remove leading //, #, *
	fm = find_front_matter(s, ext)
	sanitized = textwrap.dedent('\n'.join([parse_fm_line(line) for line in fm.splitlines()]))
	return yaml.load(sanitized) or {}

def load_front_matter(path):
	_, ext = os.path.splitext(path)
	with open(path, 'r') as f:
		return parse_front_matter(f.read(), ext[1:])
