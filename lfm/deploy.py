import os
import shutil
import tempfile
from distutils import dir_util

import boto3
import clip

import download
import utils
from lambda_config import LambdaConfig


def upload(params):
	zipfile = params['FunctionName']
	utils.make_zip(zipfile)  # Zip up directory
	with open(zipfile + ".zip", 'rb') as f:
		zip_bytes = f.read()
	# Now we're ready to upload!
	clip.echo('Deploying function "{}"...'.format(zipfile))
	client = boto3.client('lambda')
	upsert = params.pop('upsert', False)
	try:
		if upsert:
			# We can override an existing function, check if we need to
			try:
				client.get_function_configuration(FunctionName=zipfile)
				# If we made it here, we need to update
				response = client.update_function_code(FunctionName=zipfile, ZipFile=zip_bytes)
				clip.echo('Update code response: {}'.format(
					response['ResponseMetadata']['HTTPStatusCode']
				))
				params.pop('Runtime', None)
				response = client.update_function_configuration(**params)
				clip.echo('Update configuration response: {}'.format(
					response['ResponseMetadata']['HTTPStatusCode']
				))
				clip.echo('ARN: {}'.format(response['FunctionArn']))
				return
			except Exception as e:
				if 'ResourceNotFoundException' not in str(e):
					raise e
		# Create the function from scratch
		params['Code'] = {
			'ZipFile': zip_bytes
		}
		response = client.create_function(**params)
		clip.echo('Create response: {}'.format(
			response['ResponseMetadata']['HTTPStatusCode']
		))
		clip.echo('ARN: {}'.format(response['FunctionArn']))
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


def handle_directory(uri, dest, kwargs):
	clip.echo('Copying directory "{}" to "{}"...'.format(uri, dest))
	dir_util.copy_tree(uri, dest)
	deploy_dir(dest, kwargs)

def handle_file(uri, dest, kwargs):
	dest = os.path.join(dest, os.path.basename(uri))
	clip.echo('Copying file "{}" to "{}"...'.format(uri, dest))
	shutil.copyfile(uri, dest)
	deploy_file(dest, kwargs)

def handle_download(uri, dest, kwargs):
	files = download.run(uri, dest)
	if len(files) == 1:
		deploy_file(os.path.join(dest, files[0]), kwargs)
	else:
		deploy_dir(dest, kwargs)


def run(uri, kwargs):
	# Create a temporary working directory
	tmpdir = None
	try:
		tmpdir = tempfile.mkdtemp()
		uri_type = utils.uri_type(uri)
		handler = uri_type if uri_type in ['directory', 'file'] else 'download'
		globals()['handle_{}'.format(handler)](uri, tmpdir, kwargs)
	except Exception as e:
		clip.echo('Deployment failed.', err=True)
		raise e
	else:
		clip.echo('Lambda function successfully deployed!')
	finally:
		# Clean up our temporary working directory
		if tmpdir:
			utils.delete_resource(tmpdir)
