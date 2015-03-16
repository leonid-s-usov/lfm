import os
import shutil
import tempfile

import boto3
import clip
import git
from giturl import *

import utils
from lambda_config import LambdaConfig


def upload(params):
	zipfile = params['FunctionName']
	utils.make_zip(zipfile)  # Zip up directory
	clip.echo('Deploying function "{}"...'.format(zipfile))
	client = boto3.client('lambda')
	with open(zipfile + ".zip", 'rb') as f:
		params['FunctionZip'] = f
		try:
			response = client.upload_function(**params)
			clip.echo('Response: {}'.format(response['ResponseMetadata']['HTTPStatusCode']))
			clip.echo('ARN: {}'.format(response['FunctionARN']))
		except Exception as e:
			clip.exit(e, err=True)

def deploy_dir(path, kwargs):
	with utils.directory(path):
		config = LambdaConfig().load_from_cwd().update_config(kwargs)
		config.verify()
		# Remove ignore paths
		for e in config.get('ignore', []) + ['.git/', '.gitignore']:
			utils.delete_resource(e)
		# Run install command
		if 'install' in config:
			utils.shell(config.get('install'))
		upload(config.get_config())

def deploy_file(path, kwargs):
	with utils.directory(os.path.dirname(path)):
		config = LambdaConfig().load_from_front_matter(path).update_config(kwargs)
		config.verify()
		upload(config.get_config())


########################################
# FUNCTION FORMAT HANDLERS
########################################

def handle_gist(gid, dest, kwargs):
	clip.echo('Downloading Gist {} to "{}"...'.format(gid, dest))
	files = utils.download_gist(gid, dest)
	if len(files) == 1:
		# Single file Gist
		deploy_file(os.path.join(dest, files[0]), kwargs)
	else:
		# Multi-file Gist
		deploy_dir(dest, kwargs)

def handle_repo(url, dest, kwargs):
	clip.echo('Cloning Git repo "{}" to "{}"...'.format(url, dest))
	git.Repo.clone_from(url, dest)
	deploy_dir(dest, kwargs)

def handle_directory(path, dest, kwargs):
	clip.echo('Copying directory "{}" to "{}"...'.format(path, dest))
	shutil.copytree(path, dest)
	deploy_dir(dest, kwargs)

def handle_file(path, dest, kwargs):
	clip.echo('Copying file "{}" to "{}"...'.format(path, dest))
	shutil.copyfile(path, dest)
	deploy_file(dest, kwargs)


def run(path, kwargs):
	# Create a temporary working directory
	tmpdir = None
	try:
		tmpdir = tempfile.mkdtemp()
		g = GitURL(path)
		if g.valid:
			if g.is_a('gist'):
				m, src, dest = handle_gist, g.repo, tmpdir
			else:
				m, src, dest = handle_repo, g.to_ssh(), os.path.join(tmpdir, g.repo)
		else:
			m = handle_directory if os.path.isdir(path) else handle_file
			src, dest = path, os.path.join(tmpdir, os.path.basename(path))
		m(src, dest, kwargs)
	except Exception as e:
		clip.echo('Deployment failed.', err=True)
		raise e
	else:
		clip.echo('Lambda function successfully deployed!')
	finally:
		# Clean up our temporary working directory
		if tmpdir:
			utils.delete_resource(tmpdir)
