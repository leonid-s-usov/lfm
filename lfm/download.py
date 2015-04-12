import json
import os

import boto3
import clip
import git
import requests
from giturl import *

import utils


requests.packages.urllib3.disable_warnings()


# Returns a list of files in the Gist
def download_gist(uri, dest):
	gid = GitURL(uri).repo
	clip.echo('Downloading Gist "{}" to "{}"...'.format(gid, dest))
	ret = []
	req = requests.get('https://api.github.com/gists/{}'.format(gid))
	res = req.json()
	for k, v in utils.iteritems(res['files']):
		ret.append(k)
		with open(os.path.join(dest, k), 'w') as f:
			f.write(v['content'])
	return ret

# Returns a shallow list of files in repo, so upstream processing works
def download_repo(uri, dest):
	url = GitURL(uri).to_ssh()
	clip.echo('Cloning Git repo "{}" to "{}"...'.format(url, dest))
	git.Repo.clone_from(url, dest)
	return os.listdir(dest)

# Returns a list of files downloaded
def download_s3(uri, dest):
	path = uri[3:]
	clip.echo('Downloading S3 resources at "{}" to "{}"...'.format(path, dest))
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

# Returns a list containing the single file downloaded, so upstream processing works
def download_url(uri, dest):
	path = uri.split('/')[-1]
	clip.echo('Downloading file "{}" to "{}"...'.format(path, dest))
	res = requests.get(uri, stream=True)
	with open(os.path.join(dest, path), 'wb') as f:
		for chunk in res.iter_content():
			f.write(chunk)
	return [path]


def run(uri, dest):
	uri_type = utils.uri_type(uri)
	if uri_type in ['directory', 'file']:
		clip.exit('Cannot download local file, exiting...')
	return globals()['download_{}'.format(uri_type)](uri, dest)
