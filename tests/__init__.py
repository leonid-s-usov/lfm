import os
import unittest


class BaseTest(unittest.TestCase):
	'''Base class for lfm tests.

	This should:
	  - Hold generic test apps and expected values, bound to self
	  - Expose generic methods useful to other tests
	'''

	def setUp(self):
		pass

	def get_fixture_path(self, name):
		return os.path.join(os.path.dirname(__file__), 'fixtures', name)

	def load_fixture(self, name):
		with open(self.get_fixture_path(name), 'r') as f:
			return f.read()
