import os

import boto3
import clip

import deploy
import download
import init
import utils


__version__ = '0.1.0'


########################################
# COMMAND LINE APP
########################################

app = clip.App()

def print_version(value):
	clip.exit('lfm version {}'.format(__version__))

@app.main(description='The AWS Lambda Function Manager')
@clip.flag('--version', callback=print_version, hidden=True, help='Print the version')
@clip.opt('-p', '--profile', help='Set the AWS profile to use', inherit_only=True)
def lfm():
	pass

@lfm.subcommand(name='deploy', description='Deploy a Lambda function', inherits=['-p'])
@clip.arg('uri', default=os.getcwd(), help='URI of the function to deploy')
@clip.opt('-n', '--name', name='FunctionName', help='Name of the function')
@clip.opt('-r', '--role', name='Role', help='ARN of the function\'s IAM role')
@clip.opt('-x', '--handler', name='Handler', help='Function that Lambda calls to begin execution')
@clip.opt('-d', '--description', name='Description', help='A short, user-defined function description')
@clip.opt('-t', '--runtime', name='Runtime', help='Runtime environment for the Lambda function')
@clip.opt('-o', '--timeout', name='Timeout', type=int, help='Function execution time')
@clip.opt('-s', '--size', name='MemorySize', type=int, help='Function memory (MB)')
def lfm_deploy(uri, **kwargs):
	if kwargs['profile'] is not None:
		boto3.setup_default_session(profile_name=kwargs['profile'])
		del kwargs['profile']
	deploy.run(uri, {k: v for k, v in utils.iteritems(kwargs) if v})

@lfm.subcommand(name='download', description='Download a Lambda function locally', inherits=['-p'])
@clip.arg('uri', required=True, help='URI of the function to download')
@clip.opt('-d', '--dest', default=os.getcwd(), help='Where to download the function')
def lfm_download(uri, dest, profile):
	if profile is not None:
		boto3.setup_default_session(profile_name=profile)
	download.run(uri, dest)

@lfm.subcommand(name='init', description='Interactively create a .lambda.yml file')
def lfm_init():
	init.run()


########################################
# MAIN METHOD
########################################

def main(args=None):
	err = None
	try:
		app.run(args)
	except clip.ClipExit:
		# Parser-level exception, such as help/version or unrecognized argument
		pass
	except Exception as e:
		err = e
		clip.echo(e, err=True)
	finally:
		# Do any last-minute cleanup
		pass

if __name__ == '__main__':
	main()
