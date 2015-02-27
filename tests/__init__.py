import unittest


class BaseTest(unittest.TestCase):
	'''Base class for lfm tests.

	This should:
	  - Hold generic test apps and expected values, bound to self
	  - Expose generic methods useful to other tests
	'''

	def setUp(self):
		pass
