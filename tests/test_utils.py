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


class TestFrontMatter(BaseTest):

	fixtures = [
		'fm-js-1.js',          # JavaScript single-line comment block
		'fm-js-2.js',          # JavaScript multi-line comment
		'fm-js-3.js',          # JavaScript multi-line sanity check
		'fm-coffee-1.coffee',  # CoffeeScript
	]

	def _find_fm_test(self, name):
		prefix, ext = os.path.splitext(name)
		actual = self.load_fixture(name)
		expected = self.load_fixture('{}-find-expected{}'.format(prefix, ext))
		self.assertEqual(utils.find_front_matter(actual, ext[1:]), expected)

	def _parse_fm_test(self, name):
		prefix, ext = os.path.splitext(name)
		actual = self.load_fixture(name)
		expected = json.loads(self.load_fixture('fm-parse-expected.json'))
		self.assertEqual(utils.parse_front_matter(actual, ext[1:]), expected)

	def test_find_front_matter(self):
		for fixture in self.fixtures:
			self._find_fm_test(fixture)

	def test_parse_front_matter(self):
		for fixture in self.fixtures:
			self._parse_fm_test(fixture)

	def test_load_front_matter(self):
		expected = json.loads(self.load_fixture('fm-parse-expected.json'))
		for fixture in self.fixtures:
			self.assertEqual(utils.load_front_matter(self.get_fixture_path(fixture)), expected)

	def test_front_matter_errors(self):
		# Unrecognized file extension
		self.assertEqual(utils.find_front_matter('boop', '.cake'), '')
		self.assertEqual(utils.parse_front_matter('boop', '.cake'), {})
