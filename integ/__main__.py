import json
import shlex
import subprocess
import time

import boto3


class IntegManager:

	def __init__(self):
		self._total = 0
		self._successful = 0

	def register_test(self, name):
		self._total += 1
		log_info('Running test: {}'.format(name))

	def register_success(self, name):
		self._successful += 1
		log_success('Passed: {}'.format(name))

	def print_summary(self):
		print('\nTests complete, {} of {} passed\n'.format(self._successful, self._total))

integ_manager = IntegManager()


def log_info(message):
	print('[ INTEG ] {}'.format(message))

def log_nested(message):
	print('\n'.join([(4 * ' ') + line for line in message.split('\n')]))

def log_warn(message):
	print('[ WARNING ] {}'.format(message))

def log_success(message):
	print('[ SUCCESS ] {}'.format(message))

def log_fail(message):
	print('[ FAIL ] {}'.format(message))


def release_function(name):
	try:
		boto3.client('lambda').delete_function(FunctionName=name)
	except:
		log_warn('Could not release function "{}"!'.format(name))


def lfm_command(command):
	shlexed = shlex.split('env/bin/python lfm {}'.format(command))
	output = subprocess.check_output(shlexed, stderr=subprocess.STDOUT)
	log_nested(output)

def lfm_deploy_test(name, uri):
	def wrap(f):
		def wrapped_f():
			integ_manager.register_test(name)
			try:
				unique_name = '{}-{}'.format(int(time.time()), name)
				lfm_command('deploy {} -n {}'.format(uri, unique_name))
				f(unique_name)
				integ_manager.register_success(name)
			except Exception as e:
				log_fail(e)
			finally:
				log_info('Cleaning up: {}'.format(name))
				release_function(unique_name)
		return wrapped_f
	return wrap

def lfm_invoke(args, expected):
	def wrap(f):
		def wrapped_f(unique_name):
			result = boto3.client('lambda').invoke(FunctionName=unique_name, Payload=json.dumps(args))
			status = result['StatusCode']
			payload = result['Payload'].read()
			if status != 200:
				raise Exception('Invoke failed with status: {}'.format(status))
			if payload != expected:
				raise Exception('Invoke returned {}, expected {}'.format(payload, expected))
			f(unique_name)
		return wrapped_f
	return wrap


########################################
# THE ACTUAL TESTS
########################################

@lfm_deploy_test('integ-local-file', 'integ/fixtures/hello-world.js')
@lfm_invoke({}, '"Hello World from lfm integ!"')
def test_local_file(unique_name):
	pass

@lfm_deploy_test('integ-gist', 'gist:willyg302/560ab5d328b37d2cd4cc')
@lfm_invoke({
	'enc': True,
	'message': 'Hey there',
	'pass': 'password'
}, '"KVQnk+5bHpt8PMsZy2DPww=="')
def test_gist(unique_name):
	pass


########################################
# MAIN
########################################

# Run all methods prefixed with `test_`
for e in dir():
	if e.startswith('test_'):
		globals()[e]()

integ_manager.print_summary()



'''
@TODO Everything

Git repo	We just covered this, bro
GitHub Gist, 1 file	lfm deploy gist:willyg302/25b8f32e6784aca03a27
GitHub Gist, 2+ files	lfm deploy gist:willyg302/560ab5d328b37d2cd4cc
Local file	lfm deploy awesome-sauce.js
Local directory	lfm deploy my-sweet-function/
Working directory	lfm deploy
S3 bucket	lfm deploy s3:mah-bucket
File on S3	lfm deploy s3:mah-bucket/hello-world.js
Directory on S3	lfm deploy s3:mah-bucket/my-function


'''