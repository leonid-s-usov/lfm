from mock import patch

from . import BaseTest
from lfm import init


class TestInit(BaseTest):

	@patch('lfm.init.clip.echo')
	@patch('lfm.init.LambdaConfig')
	def test_run(self, config, _):
		instance = config.return_value.load_from_cwd.return_value
		with self.mock_clip_input(['hello-world', 'index.handler', '', '', '', '64', 'make']):
			init.run()
			instance.update_config.assert_called_with({
				'FunctionName': 'hello-world',
				'Handler': 'index.handler',
				'MemorySize': 64,
				'Runtime': 'nodejs'
			})
			instance.update.assert_called_with({
				'install': 'make'
			})
			instance.dump_to_cwd.assert_called_with()
