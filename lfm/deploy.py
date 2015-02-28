import os
import shutil
import tempfile

import boto3
import clip
import git
from giturl import *

import utils


def upload(zipfile, params):
	clip.echo('Deploying function "{}"...'.format(params['FunctionName']))
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
		config = utils.load_config()
		config['config'].update(kwargs)
		if 'FunctionName' not in config['config']:
			clip.exit('You must provide a function name', err=True)
		# Remove ignore paths
		for e in config.get('ignore', []) + ['.git/', '.gitignore']:
			utils.delete_resource(e)
		# Run install command
		if 'install' in config:
			utils.shell(config['install'])
		# Zip up directory
		utils.make_zip(config['config']['FunctionName'])
		# Upload!
		params = config['config']
		upload(params['FunctionName'], params)

def deploy_file(path, kwargs, config):
	with utils.directory(os.path.dirname(path)):
		config.update(kwargs)
		if 'FunctionName' not in config:
			clip.exit('You must provide a function name', err=True)
		# Zip up directory
		utils.make_zip(config['FunctionName'])
		# Upload!
		upload(config['FunctionName'], config)

def run(path, kwargs):
	# Create a temporary working directory
	tmpdir = None
	try:
		tmpdir = tempfile.mkdtemp()
		g = GitURL(path)
		if g.valid:
			if g.is_a('gist'):
				# GitHub Gist
				gid = g.repo
				dest = tmpdir
				clip.echo('Downloading Gist {} to "{}"...'.format(gid, dest))
				files = utils.download_gist(gid, dest)
				if len(files) == 1:
					# Single file Gist
					parsed_dest = os.path.join(tmpdir, files[0])
					parsed = utils.load_front_matter(parsed_dest)
					deploy_file(parsed_dest, kwargs, parsed)
				else:
					# Multi-file Gist
					deploy_dir(dest, kwargs)
			else:
				# Git repo
				url = g.to_ssh()
				dest = os.path.join(tmpdir, g.repo)
				clip.echo('Cloning Git repo "{}" to "{}"...'.format(url, dest))
				git.Repo.clone_from(url, dest)
				deploy_dir(dest, kwargs)
		elif os.path.isdir(path):
			# Directory
			dest = os.path.join(tmpdir, os.path.basename(path))
			clip.echo('Copying directory "{}" to "{}"...'.format(path, dest))
			shutil.copytree(path, dest)
			deploy_dir(dest, kwargs)
		else:
			# File
			dest = os.path.join(tmpdir, os.path.basename(path))
			parsed = utils.load_front_matter(path)
			clip.echo('Copying file "{}" to "{}"...'.format(path, dest))
			shutil.copyfile(path, dest)
			deploy_file(dest, kwargs, parsed)
	except Exception as e:
		clip.echo('Deployment failed.', err=True)
		raise e
	else:
		clip.echo('Lambda function successfully deployed!')
	finally:
		# Clean up our temporary working directory
		if tmpdir:
			utils.delete_resource(tmpdir)
