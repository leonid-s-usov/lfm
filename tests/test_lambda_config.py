import clip

from mock import Mock, mock_open, patch

from . import BaseTest
from lfm.lambda_config import LambdaConfig, load_yaml


mock_config = {
	'config': {
		'foo': 'baz',
		'bar': 'qux'
	},
	'joe': 'bob'
}


class TestLambdaConfig(BaseTest):

	@patch('lfm.lambda_config.os.path.isfile', side_effect=[True, False, False])
	def test_load_yaml(self, isfile):
		with patch('__builtin__.open', mock_open(), create=True) as file_mock:
			self.assertEqual(load_yaml('djibouti'), {})
			file_mock.assert_any_call('djibouti', 'r')
			# Defaults
			self.assertEqual(load_yaml('nope'), {})
			self.assertEqual(load_yaml('nope again', { 'jk': 'yes'}), { 'jk': 'yes' })

	def test_getters(self):
		config = LambdaConfig().update(mock_config)
		self.assertTrue('joe' in config)
		# get()
		self.assertEqual(config.get('joe'), 'bob')
		self.assertIsNone(config.get('jim'))
		self.assertEqual(config.get('jim', 5), 5)
		# get_config()
		self.assertEqual(config.get_config(), mock_config['config'])
		self.assertEqual(config.get_config('foo'), 'baz')
		self.assertIsNone(config.get_config('sam'))
		self.assertEqual(config.get_config('sam', 5), 5)

	def test_updates(self):
		config = LambdaConfig().update(mock_config).update({
			'config': {
				'foo': 3
			},
			'joe': 4,
			'jim': 5
		})
		self.assertEqual(config.get_config('foo'), 3)
		self.assertEqual(config.get('joe'), 4)
		self.assertEqual(config.get('jim'), 5)
		self.assertEqual(config.update_config({
			'bar': 6
		}).get_config('bar'), 6)

	def test_load_from_cwd(self):
		# If no config is present
		self.assertEqual(LambdaConfig().load_from_cwd()._config, {
			'config': {},
			'ignore': []
		})

	@patch('lfm.lambda_config.clip.echo')
	def test_verify(self, _):
		with self.assertRaises(clip.ClipExit):
			LambdaConfig().verify()
		with self.assertRaises(clip.ClipExit):
			LambdaConfig().update(mock_config).verify()
		# @TODO: Test global role loading logic
