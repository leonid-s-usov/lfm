import os
import clip

from mock import patch

from . import BaseTest
from lfm import cli


class TestCli(BaseTest):

	@patch('lfm.cli.clip.exit')
	def test_version(self, clip_exit):
		cli.app.run('--version')
		self.assertTrue(clip_exit.call_args[0][0].startswith('lfm version'))

	@patch('lfm.cli.deploy.run')
	@patch('lfm.cli.boto3.setup_default_session')
	def test_deploy(self, profile, run):
		# No arguments
		cli.app.run('deploy')
		run.assert_called_with(os.getcwd(), {})
		# Path
		cli.app.run('deploy some/dir')
		run.assert_called_with('some/dir', {})
		# Configiness
		cli.app.run('deploy -n yo --role mah:role -o 256 -x index.handler booyah')
		run.assert_called_with('booyah', {
			'FunctionName': 'yo',
			'Role': 'mah:role',
			'Handler': 'index.handler',
			'Timeout': 256
		})
		# Custom AWS profile
		cli.app.run('deploy cake -p aws')
		profile.assert_called_with(profile_name='aws')
		run.assert_called_with('cake', {})

	@patch('lfm.cli.clip.echo')
	@patch('lfm.cli.download.run')
	@patch('lfm.cli.boto3.setup_default_session')
	def test_download(self, profile, run, _):
		# URI required
		with self.assertRaises(clip.ClipExit):
			cli.app.run('download')
		# Default dest
		cli.app.run('download something')
		run.assert_called_with('something', os.getcwd())
		# Specified dest
		cli.app.run('download something -d here')
		run.assert_called_with('something', 'here')
		# Custom AWS profile
		cli.app.run('-p aws download something -d here')
		profile.assert_called_with(profile_name='aws')
		run.assert_called_with('something', 'here')

	@patch('lfm.cli.init.run')
	def test_init(self, run):
		cli.app.run('init')
		run.assert_called_with()
