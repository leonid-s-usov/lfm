import collections

import clip

import utils


class LambdaConfig:
	
	def __init__(self):
		self._config = {}

	def __contains__(self, key):
		return key in self._config

	def get(self, key, default=None):
		return self._config.get(key, default)

	def get_config(self, key=None):
		if key is None:
			return self.get('config')
		return self.get('config')[key]

	def load_from_cwd(self):
		return self.update(utils.load_config())

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
		self.get('config').update(d)
		return self

	def verify(self):
		if 'FunctionName' not in self.get_config():
			clip.exit('You must provide a function name', err=True)
