import collections
import os

import clip
import yaml

import utils


CONFIG = 'lambda.yml'


def load_yaml(path, default={}):
	ret = None
	if os.path.isfile(path):
		with open(path, 'r') as f:
			ret = yaml.load(f)
	return ret or default


class LambdaConfig:
	'''Manages configuration information for a Lambda function.

	Config may come from several sources:
	  - Global config in ~/.aws/lambda.yml
	  - Local project-specific .lambda.yml or front matter
	  - Command line arguments

	Keys should take precedence in the order above; e.g. command line
	arguments should be applied last and override previous config settings.

	Note that a LambdaConfig object itself holds a key called `config`
	that contains information one would normally pass to the AWS CLI.
	Do not confuse this with other mentions of configuration in general.
	'''

	def __init__(self):
		self._config = {
			'config': {}
		}
		self._global_config = load_yaml(os.path.join(os.path.expanduser('~'), '.aws', CONFIG))

	def __contains__(self, key):
		return key in self._config

	def get(self, key, default=None):
		return self._config.get(key, default)

	def get_config(self, key=None, default=None):
		if key is None:
			return self.get('config')
		return self.get('config').get(key, default)

	def load_from_cwd(self):
		return self.update(load_yaml("." + CONFIG, {
			'config': {},
			'ignore': []
		}))

	def load_from_front_matter(self, path):
		return self.update(utils.load_front_matter(path))

	def update(self, d):
		def _nested_update(d, u):
			for k, v in u.iteritems():
				if isinstance(v, collections.Mapping):
					r = _nested_update(d.get(k, {}), v)
					d[k] = r
				else:
					d[k] = u[k]
			return d
		_nested_update(self._config, d)
		return self

	def update_config(self, d):
		self.get_config().update(d)
		return self

	def verify(self):
		if self.get_config() is None:
			clip.exit('Configuration has not been specified!', err=True)
		if 'FunctionName' not in self.get_config():
			clip.exit('You must provide a function name', err=True)
		# Fill in from global config
		if self._global_config:
			role = self.get_config('Role', 'default')
			if not role.startswith('arn:aws:iam::'):
				roles = self._global_config.get('roles')
				if roles and role in roles:
					self._config['config']['Role'] = roles[role]
