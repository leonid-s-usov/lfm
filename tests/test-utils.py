import os
import json

from mock import Mock, mock_open, patch

from . import BaseTest
from lfm import utils


mock_gist = json.dumps({
	'files': {
		'foo': {
			'content': 'baz'
		},
		'bar': {
			'content': 'qux'
		}
	}
})


class TestUtils(BaseTest):

	def test_directory(self):
		cwd = os.getcwd()
		with utils.directory('tests'):
			self.assertEqual(os.getcwd(), os.path.join(cwd, 'tests'))
		self.assertEqual(os.getcwd(), cwd)

	def test_load_config(self):
		# If no config is present
		self.assertEqual(utils.load_config(), {
			'config': {},
			'ignore': []
		})

	@patch('lfm.utils.os.path.isfile', side_effect=[True, False])
	@patch('lfm.utils.os.path.isdir', side_effect=[True])
	@patch('lfm.utils.os.remove')
	@patch('lfm.utils.shutil.rmtree')
	def test_delete_resource(self, rmtree, remove, isdir, isfile):
		utils.delete_resource('folder')
		remove.assert_called_with('folder')
		utils.delete_resource('directory')
		rmtree.assert_called_with('directory', ignore_errors=True)

	@patch('lfm.utils.urllib2.urlopen')
	def test_download_gist(self, urlopen):
		m = Mock()
		m.read.side_effect = [mock_gist]
		urlopen.return_value = m
		with patch('__builtin__.open', mock_open()) as file_mock:
			ret = utils.download_gist('9001', 'some/dir')
			self.assertEqual(ret, ['foo', 'bar'])
			file_mock.assert_any_call('some/dir/foo', 'w')
			file_mock.assert_any_call('some/dir/bar', 'w')
			write = file_mock().write
			write.assert_any_call('baz')
			write.assert_any_call('qux')
