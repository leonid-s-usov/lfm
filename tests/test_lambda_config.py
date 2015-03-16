from . import BaseTest
from lfm.lambda_config import LambdaConfig


class TestLambdaConfig(BaseTest):

	def test_load_from_cwd(self):
		# If no config is present
		self.assertEqual(LambdaConfig().load_from_cwd()._config, {
			'config': {},
			'ignore': []
		})
