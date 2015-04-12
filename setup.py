'''
lfm
---
lfm is the `AWS Lambda <http://aws.amazon.com/lambda/>`_ Function Manager.
Deploy your functions directly from a local directory or Git repo!
'''
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='lfm',
	version='0.1.0',
	url='https://github.com/willyg302/lfm',
	license='MIT',
	author='William Gaul',
	author_email='willyg302@gmail.com',
	description='The AWS Lambda Function Manager',
	long_description=__doc__,
	packages=['lfm'],
	test_suite='tests',
	platforms='any',
	install_requires=[
		'bcdoc==0.12.2',
		'boto3==0.0.14',
		'botocore==0.102.0',
		'clip.py==0.2.1',
		'docutils==0.12',
		'gitdb==0.6.4',
		'GitPython==0.3.6',
		'giturl.py==0.2.1',
		'jmespath==0.6.1',
		'python-dateutil==2.4.0',
		'PyYAML==3.11',
		'requests==2.6.0',
		'six==1.9.0',
		'smmap==0.9.0',
	],
	tests_require=[
		'mock==1.0.1',
	],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.4',
	],
	entry_points={
		'console_scripts': [
			'lfm = lfm.cli:main'
		]
	}
)
